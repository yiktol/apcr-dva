#!/usr/bin/env python3
"""Local dev server for the APCR-DVA Knowledge Check WITH a real AI judge.

Plain `python3 -m http.server` (or serve.sh) serves the static files only --
no backend, so knowledgecheck.html's /judge call always fails fast and the
viewer silently falls back to its local, canned explanations. This server
serves site/ AND answers POST /judge for real: it fetches the live AWS doc
page(s) cited in the question's `sources`, hands their text plus the
question/options/keyed-answer to Amazon Bedrock (Converse API, Claude Sonnet
4.5), and returns the model's doc-grounded verdict. No mocks, no canned
responses -- if Bedrock or the doc fetch fails, the handler returns a well
-formed `{"error": ..., "grounded": false}` body (still HTTP 200) and the
viewer degrades to local explanations exactly as it does with plain
serve.sh.

Credentials: uses boto3's default credential chain (environment, shared
config/SSO profile, instance role, etc.) -- nothing is hardcoded here. Run
`aws sso login` (or otherwise have ambient AWS creds) before starting this
server if Bedrock calls need to succeed.

Usage:
    python3 serve_with_judge.py [PORT]        # default 8030

Then open:  http://localhost:8030/knowledgecheck.html?m=1
and answer a "Check yourself" question -- a "Checking against AWS docs..."
line appears under the local feedback, then real per-option verdicts and
citations render once Bedrock responds.

See also: serve.sh (static-only mode -- no /judge backend, local
explanations only; this is the "judge absent" fallback path).
"""
from __future__ import annotations

import html.parser
import http.server
import json
import os
import re
import socketserver
import sys
import urllib.error
import urllib.request

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8030
DIR = os.path.dirname(os.path.abspath(__file__))

AWS_REGION = "us-east-1"
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"  # inference-profile
# prefix "us." is required -- the bare "anthropic.*" model id fails.

MAX_SOURCES = 3
DOC_CHAR_CAP = 15000
FETCH_TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

SYSTEM_PROMPT = """You are an AWS certification answer-key author. A learner \
has just picked an option. You are given the question, its options, the \
option the learner picked, the answer key's correct answer, a short static \
rationale, whether the pick was correct, and excerpts fetched live from \
official AWS documentation pages.

Write a DIRECT verdict on the LEARNER'S PICKED OPTION, in the exact style of \
an exam answer key. Match this style precisely:

  "Correct. Lambda functions can be invoked from S3 events and can read from \
S3 buckets. An event-based invocation allows the S3 objects to be processed \
as soon as they arrive."

  "Incorrect. Lambda functions can run on a schedule and connect to Amazon \
EFS file systems. However, a scheduled or polling process would not process \
the files as soon as they arrive."

Rules for the "explanation" text:
- Begin with exactly "Correct." or "Incorrect." (based on the `correct` \
flag), then one or two factual sentences stating WHY the picked option is or \
is not right.
- Be direct and declarative. State facts. Do NOT coach, do NOT ask questions, \
do NOT say "consider", "think about", "reconsider", or "look again". Do NOT \
address the learner ("you"). No preamble, no filler.
- For an INCORRECT pick, explain why THAT option is wrong on its own terms. \
You do not need to hide the correct answer, but keep the focus on the picked \
option -- do not enumerate the other options.
- Ground every claim in the provided documentation excerpts. If no excerpts \
were provided, state the fact from general AWS knowledge accurately.
- Plain text only, no markdown.

Separately, pick the single most relevant source URL from the provided \
documentation excerpts for this verdict (or null if none was provided).

Respond with STRICT JSON ONLY -- no prose before or after, no markdown code \
fences -- in exactly this shape:
{"explanation": "Correct. ...", "citation": "https://docs.aws.amazon.com/... or null"}
"explanation" is a single plain-text string; "citation" is one URL string \
drawn from the provided excerpts, or null."""


# ---------------------------------------------------------------------------
# HTML -> visible text
# ---------------------------------------------------------------------------

class _TextExtractor(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0 and data.strip():
            self._parts.append(data.strip())

    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self._parts)).strip()


def strip_html(html_text: str) -> str:
    """Drop <script>/<style> content and all tags, collapse whitespace,
    return the visible text."""
    parser = _TextExtractor()
    try:
        parser.feed(html_text)
    except Exception:
        pass
    return parser.text()


# ---------------------------------------------------------------------------
# Live doc fetch
# ---------------------------------------------------------------------------

def fetch_doc(url: str, cap: int = DOC_CHAR_CAP, timeout: int = FETCH_TIMEOUT) -> str | None:
    """Fetch a live AWS doc page and return its stripped visible text,
    truncated to `cap` chars. Returns None on any failure (bad status,
    network error, timeout, decode error) -- never raises."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            raw = resp.read()
    except Exception:
        return None
    try:
        text = raw.decode("utf-8", errors="replace")
    except Exception:
        return None
    stripped = strip_html(text)
    if not stripped:
        return None
    return stripped[:cap]


# ---------------------------------------------------------------------------
# Bedrock
# ---------------------------------------------------------------------------

def bedrock_client():
    import boto3  # imported lazily so the server can still start without it
    return boto3.client("bedrock-runtime", region_name=AWS_REGION)


def extract_first_json(text: str) -> dict | None:
    """Find the first balanced {...} block in `text` and json.loads it.
    Returns None on failure."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start:i + 1]
                try:
                    return json.loads(candidate)
                except Exception:
                    return None
    return None


def build_user_message(payload: dict, docs: list[tuple[str, str]]) -> str:
    # Reference "choice" contract: a single learner pick is judged for a
    # Socratic nudge (wrong) or grounded affirmation (correct).
    options = payload.get("options") or []
    if options and isinstance(options[0], dict):
        opts_text = "\n".join(f"{o.get('letter')}: {o.get('text')}" for o in options)
    else:
        opts_text = "\n".join(str(o) for o in options)
    pick = payload.get("pick", "")
    answer = payload.get("answer", "")
    why = payload.get("why", "")
    correct = bool(payload.get("correct"))
    if docs:
        doc_text = "\n\n".join(
            f"--- DOC EXCERPT ({url}) ---\n{text}" for url, text in docs
        )
    else:
        doc_text = "(no documentation excerpts were available -- answer from general AWS knowledge only)"
    return (
        f"QUESTION:\n{payload.get('prompt', '')}\n\n"
        f"OPTIONS:\n{opts_text}\n\n"
        f"LEARNER PICKED: {pick}\n"
        f"LEARNER WAS: {'CORRECT' if correct else 'WRONG'}\n"
        f"CORRECT ANSWER (do NOT reveal if the learner was wrong): {answer}\n"
        f"STATIC RATIONALE (for your reference only): {why}\n\n"
        f"DOCUMENTATION EXCERPTS:\n{doc_text}\n"
    )


def run_judge(payload: dict) -> dict:
    """Fetch up to the first MAX_SOURCES `sources`, ask Bedrock to judge the
    question against them, and return the response dict. Never raises --
    any exception is caught and turned into {"error": ..., "grounded": False}."""
    try:
        sources = (payload.get("sources") or [])[:MAX_SOURCES]
        docs: list[tuple[str, str]] = []
        for url in sources:
            text = fetch_doc(url)
            if text:
                docs.append((url, text))
        sources_used = [url for url, _ in docs]
        grounded = len(sources_used) > 0

        user_message = build_user_message(payload, docs)
        client = bedrock_client()

        def call(temperature: float) -> dict | None:
            response = client.converse(
                modelId=MODEL_ID,
                messages=[{"role": "user", "content": [{"text": user_message}]}],
                system=[{"text": SYSTEM_PROMPT}],
                inferenceConfig={"maxTokens": 1500, "temperature": temperature},
            )
            out_text = response["output"]["message"]["content"][0]["text"]
            return extract_first_json(out_text)

        result = call(0.3)
        if result is None:
            result = call(0.0)
        if result is None:
            return {"error": "judge: could not parse an explanation from the model response", "grounded": False}

        explanation = (result.get("explanation") or "").strip()
        if not explanation:
            return {"error": "judge: empty explanation", "grounded": False}
        # Only trust a citation that is actually one of the pages we fetched,
        # so the model can't fabricate a plausible-looking doc URL.
        citation = result.get("citation")
        if citation not in sources_used:
            citation = sources_used[0] if sources_used else None
        return {
            "explanation": explanation,
            "citation": citation,
            "grounded": bool(grounded),
            "sourcesUsed": sources_used,
        }
    except Exception as e:
        return {"error": str(e), "grounded": False}


# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=DIR, **k)

    def do_POST(self):
        if self.path.rstrip("/") != "/judge":
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception as e:
            payload = None
            parse_error = str(e)
        if payload is None:
            result = {"error": f"invalid JSON body: {parse_error}", "grounded": False}
        else:
            result = run_judge(payload)
        out = json.dumps(result).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(out)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.end_headers()

    # end_headers runs for every response, so set the always-on headers here
    # (Cache-Control + CORS origin) rather than repeating them per handler.
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


class TCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    print(f"Serving {DIR} at http://localhost:{PORT}/")
    print(f"  /judge  ->  real Bedrock Converse judge  (model={MODEL_ID}, region={AWS_REGION})")
    print(f"Open: http://localhost:{PORT}/knowledgecheck.html?m=1")
    print("Ctrl-C to stop.")
    with TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
