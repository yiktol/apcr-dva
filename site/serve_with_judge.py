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

SYSTEM_PROMPT = """You are an AWS certification answer-key reviewer. You are \
given an exam question, its answer options, the answer key's claimed \
correct letter(s), and excerpts fetched live from official AWS \
documentation pages. Your job is to judge, strictly from the provided doc \
excerpts (not general knowledge), whether each option is correct or \
incorrect, whether the docs support the keyed answer, and whether the key \
appears to be outdated versus the current docs.

Respond with STRICT JSON ONLY -- no prose before or after, no markdown code \
fences -- in exactly this shape:
{
  "perOption": [
    {"letter": "A", "verdict": "correct|incorrect", "why": "...", "citedSource": "<url or null>"}
  ],
  "docSupportedCorrect": ["C"],
  "keyAgreesWithDocs": true,
  "keyNote": "...",
  "grounded": true
}
Field names and nesting must match exactly. "perOption" must have one entry \
per option letter given, in the same order. "docSupportedCorrect" is the \
list of letters the docs actually support as correct. "keyAgreesWithDocs" \
is true only if docSupportedCorrect matches the keyed correct letters \
exactly. "keyNote" briefly explains your reasoning, and must call out \
clearly if the keyed answer looks outdated vs. the current docs. Set \
"grounded" to true if you relied on the provided doc excerpts, false if no \
usable excerpts were provided and you are answering from general knowledge \
only."""


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
    options = payload.get("options") or []
    opts_text = "\n".join(f"{o.get('letter')}: {o.get('text')}" for o in options)
    keyed = ", ".join(payload.get("keyedCorrect") or [])
    if docs:
        doc_text = "\n\n".join(
            f"--- DOC EXCERPT ({url}) ---\n{text}" for url, text in docs
        )
    else:
        doc_text = "(no documentation excerpts were available -- answer from general AWS knowledge only, and set grounded to false)"
    return (
        f"QUESTION:\n{payload.get('prompt', '')}\n\n"
        f"OPTIONS:\n{opts_text}\n\n"
        f"ANSWER KEY CLAIMS CORRECT: {keyed}\n\n"
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

        result = call(0.2)
        if result is None:
            result = call(0.0)
        if result is None:
            return {"error": "judge: could not parse a JSON verdict from the model response", "grounded": False}

        result["grounded"] = bool(grounded) and bool(result.get("grounded", True))
        if not grounded:
            result["keyNote"] = (result.get("keyNote", "") + " (model knowledge only -- no documentation excerpts were fetched successfully)").strip()
        result["sourcesUsed"] = sources_used
        return result
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
