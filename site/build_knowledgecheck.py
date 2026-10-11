#!/usr/bin/env python3
"""
Build the per-session Knowledge Check decks for knowledgecheck.html by
parsing the five Content Review markdown files under ../md and emitting one
slide-array bundle per session (knowledgecheck/d<N>.{json,js}), in the same
dual-emit shape as site/build_decks.py and the reference
aib-c01/build_knowledgecheck.py.

Source files (one per session, see CONTENT_REVIEW below):
    ../md/session1/02 - APCR-DVA - Content Review Session 1.md
    ../md/session2/03 - APCR-DVA - Content Review Session 2.md
    ../md/session3/04 - APCR-DVA - Content Review Session 3.md
    ../md/session4/05 - APCR-DVA - Content Review Session 4.md
    ../md/session5/06 - APCR-DVA - Content Review Session 5.md

Each file is a sequence of "## Slide N — <title>" blocks (an image plus a
"### Notes" section). The practice questions appear near the end of each
file as a run of 4 consecutive slides that all share the exact same title
"Question K: <short title>": a timed stem slide, a "key phrases" slide, a
"reveal" slide, and an "elimination" slide.

The reveal slide's Notes hold everything needed to build the question:
  - A line "ANSWER OVERVIEW: [Tt]he answer is X." (or multi-answer
    "...is A and B." / "...is A, B, and C.") -- the authoritative correct
    letter(s).
  - One paragraph per option, in the form
    "A. <clean option text> — Correct — <rationale>" or
    "A. <clean option text> — Incorrect — <rationale>" (em-dash delimited).
    The text before the first em-dash is the clean option text; the
    Correct/Incorrect word must agree with the ANSWER OVERVIEW line; the
    text after the second em-dash is that option's rationale.

Each question's first slide also carries a "### Question" markdown block
(injected from the original .pptx slide body by temp/enrich_stems.py) with
the full on-slide scenario paragraph(s) and the trailing "Which ...?" line,
followed by a blank line and the lettered option list. That scenario text
(everything before the first lettered option line) is used verbatim as the
question prompt; the title string is only a fallback for the rare case a
block is missing.

Doc reference URLs: every full "https://docs.aws.amazon.com/..." URL that
appears anywhere in the question's own 4-slide block (most often on a
"REFERENCE:"/"SOURCE:" line on the reveal or elimination slide, sometimes a
second URL on an "Also verified against:" line) is captured as that
question's source, deduplicated, in first-seen order.

A question is skipped (and reported on stderr) if its block has no reveal
slide, no ANSWER OVERVIEW line, or if the Correct/Incorrect markers on its
option paragraphs disagree with the ANSWER OVERVIEW letters -- no answer,
option text, rationale or URL is ever invented.

Usage:  python3 build_knowledgecheck.py   (run from the site/ directory, or
        anywhere -- paths are resolved relative to this script's location)
"""
from __future__ import annotations

import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MD_DIR = os.path.join(HERE, "..", "md")
OUTDIR = os.path.join(HERE, "knowledgecheck")

SESSIONS = {
    1: ("session1", "Infrastructure Foundations"),
    2: ("session2", "Development with AWS Services"),
    3: ("session3", "Decoupling, Caching, Auth & Observability"),
    4: ("session4", "Testing and Deployment"),
    5: ("session5", "Security, AI Security & Observability"),
}

# One "Content Review Session N.md" file per session -- the sole question
# source (the Exam Strategy answer-key files were retired). See
# .agents/tasks/kc-content-review-reparse-plan.md.
CONTENT_REVIEW = {
    1: "02 - APCR-DVA - Content Review Session 1.md",
    2: "03 - APCR-DVA - Content Review Session 2.md",
    3: "04 - APCR-DVA - Content Review Session 3.md",
    4: "05 - APCR-DVA - Content Review Session 4.md",
    5: "06 - APCR-DVA - Content Review Session 5.md",
}

DOC_URL_RE = re.compile(r"https://docs\.aws\.amazon\.com/[^\s)\"'>\u00b7]+")

# Accent CSS vars, as defined in knowledgecheck.html's own :root (mirrors the
# per-session accent mapping already in site/index.html's .card.d1..d5 rules).
ACCENTS = {
    1: "var(--aws-blue)",
    2: "var(--aws-teal)",
    3: "var(--aws-navy)",
    4: "var(--aws-green)",
    5: "var(--aws-magenta)",
}

LETTERS = "ABCDEFG"

# "## Slide 51 — Question 1: Session state across instances"
SLIDE_HEADING_RE = re.compile(r"^##\s*Slide\s+\d+\s*—\s*(.*)$")
QUESTION_TITLE_RE = re.compile(r"^Question\s+(\d+):\s*(.*)$")

ANSWER_OVERVIEW_RE = re.compile(r"ANSWER OVERVIEW:\s*[Tt]he answer is\s+(.+?)\.")
OPTION_LINE_RE = re.compile(
    r"^([A-G])\.\s*(.+?)\s*—\s*(Correct|Incorrect)\s*—\s*(.+)$"
)

# "### Question" ... up to the next "### " heading or a "---" rule.
QUESTION_BLOCK_RE = re.compile(r"^### Question\s*$", re.MULTILINE)
LETTERED_OPTION_RE = re.compile(r"^[A-G]\.\s")


def extract_stem(block_lines: list[str]) -> str | None:
    """Return the full scenario paragraph from the first '### Question'
    block in this question's combined slide block, or None if no such block
    is present. The block holds the scenario prose, the trailing
    'Which ...?' line, then a blank line and the lettered option list --
    only the prose/question line (everything before the first lettered
    option) is the prompt; the options are parsed separately from the
    reveal slide."""
    text = "\n".join(block_lines)
    m = QUESTION_BLOCK_RE.search(text)
    if not m:
        return None
    rest = text[m.end():]
    # Stop at the next "### " heading or a "---" rule (end of this slide's
    # Question block), whichever comes first.
    end_m = re.search(r"^(### |---\s*$)", rest, re.MULTILINE)
    body = rest[:end_m.start()] if end_m else rest
    stem_lines = []
    for line in body.split("\n"):
        line = line.strip()
        if not line:
            continue
        if LETTERED_OPTION_RE.match(line):
            break
        stem_lines.append(line)
    stem = " ".join(stem_lines).strip()
    return stem or None


def e(s) -> str:
    return html.escape(str(s if s is not None else ""))


def strip_bold(s: str) -> str:
    s = s.strip()
    if s.startswith("**") and s.endswith("**") and len(s) >= 4:
        return s[2:-2].strip()
    return s


# ---------------------------------------------------------------------------
# Markdown -> question blocks
# ---------------------------------------------------------------------------

def paragraphs_of(block_lines: list[str]) -> list[str]:
    """Join a block's lines into blank-line-delimited paragraphs, each with
    internal newlines collapsed to single spaces."""
    text = "\n".join(block_lines)
    raw_paras = re.split(r"\n\s*\n", text)
    out = []
    for p in raw_paras:
        p = " ".join(l.strip() for l in p.split("\n") if l.strip() != "")
        if p:
            out.append(p)
    return out


def split_slides(text: str):
    """Split a Content Review markdown file into (title, body_lines) tuples,
    one per '## Slide N — <title>' heading, in document order."""
    lines = text.split("\n")
    heading_idxs = []
    for i, line in enumerate(lines):
        m = SLIDE_HEADING_RE.match(line)
        if m:
            heading_idxs.append((i, m.group(1).strip()))

    slides = []
    for idx, (line_i, title) in enumerate(heading_idxs):
        block_start = line_i + 1
        block_end = heading_idxs[idx + 1][0] if idx + 1 < len(heading_idxs) else len(lines)
        slides.append((title, lines[block_start:block_end]))
    return slides


def group_question_slides(slides: list[tuple[str, list[str]]]):
    """Group consecutive slides sharing an identical title that starts with
    'Question K: ...' into one (question_num, title, combined_lines) block
    per question, in document order. Non-"Question N:" titled slides
    (teaching slides) are skipped entirely."""
    groups = []
    i = 0
    n = len(slides)
    while i < n:
        title, lines = slides[i]
        m = QUESTION_TITLE_RE.match(title)
        if not m:
            i += 1
            continue
        qnum = int(m.group(1))
        combined = list(lines)
        j = i + 1
        while j < n and slides[j][0] == title:
            combined.extend(slides[j][1])
            j += 1
        groups.append((qnum, title, combined))
        i = j
    return groups


# ---------------------------------------------------------------------------
# Per-question extraction
# ---------------------------------------------------------------------------

def parse_answer_letters(fragment: str) -> list[str]:
    """Parse the captured text after 'the answer is' (e.g. 'A', 'A and B',
    'A, B, and C') into an ordered list of letters."""
    return re.findall(r"[A-G]", fragment)


def parse_question_block(qnum: int, title: str, block_lines: list[str], label: str):
    """Parse one question's combined 4-slide block. Returns a question dict
    in the shape check_slide()/write() expect, or None (with a reason
    printed to stderr) if the block is missing a required piece or its
    Correct/Incorrect markers disagree with the ANSWER OVERVIEW letters."""
    block_text = "\n".join(block_lines)

    m = ANSWER_OVERVIEW_RE.search(block_text)
    if not m:
        print(f"    skip {label} Q{qnum} ({title}): no ANSWER OVERVIEW line found", file=sys.stderr)
        return None
    answer_letters = parse_answer_letters(m.group(1))
    if not answer_letters:
        print(f"    skip {label} Q{qnum} ({title}): could not parse letters from "
              f"ANSWER OVERVIEW {m.group(1)!r}", file=sys.stderr)
        return None

    options = []
    marked_correct = []
    for p in paragraphs_of(block_lines):
        om = OPTION_LINE_RE.match(p.strip())
        if not om:
            continue
        letter, text, verdict, rationale = om.group(1), om.group(2).strip(), om.group(3), om.group(4).strip()
        is_correct = verdict == "Correct"
        if is_correct:
            marked_correct.append(letter)
        options.append({"letter": letter, "text": text, "rationale": rationale, "correct": is_correct})

    if not options:
        print(f"    skip {label} Q{qnum} ({title}): no option lines found on the reveal slide", file=sys.stderr)
        return None

    if sorted(marked_correct) != sorted(answer_letters):
        print(f"    skip {label} Q{qnum} ({title}): ANSWER OVERVIEW says {answer_letters} but "
              f"option Correct/Incorrect markers say {marked_correct}", file=sys.stderr)
        return None

    sources = []
    for url_m in DOC_URL_RE.finditer(block_text):
        url = url_m.group(0).rstrip(".,;")
        if url not in sources:
            sources.append(url)

    stem = extract_stem(block_lines)
    if stem is None:
        print(f"    warn {label} Q{qnum} ({title}): no '### Question' stem block found, "
              f"falling back to the slide title as the prompt", file=sys.stderr)

    return {
        "prompt": stem if stem else title,
        "options": [{"letter": o["letter"], "text": o["text"], "rationale": o["rationale"]} for o in options],
        "correct": answer_letters,
        "multi": len(answer_letters) > 1,
        "sources": sources,
    }


def parse_session_markdown(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    label = os.path.basename(path)
    slides = split_slides(text)
    questions = []
    for qnum, title, block_lines in group_question_slides(slides):
        q = parse_question_block(qnum, title, block_lines, label)
        if q is not None:
            questions.append(q)
    return questions


# ---------------------------------------------------------------------------
# Slide HTML builders (mirrors the reference's check_slide()/divider shape)
# ---------------------------------------------------------------------------

def divider_slide(session_n: int, title: str, count: int) -> str:
    accent = ACCENTS[session_n]
    return (
        f'<div class="slide-native section-header sm-divider" style="--accent:{accent};">'
        f'<div class="kicker">Session {session_n} &middot; Knowledge Check</div>'
        f'<h2>{e(title)}</h2>'
        f'<div class="sm-divider-meta">{count} questions</div>'
        "</div>"
    )


def check_slide(session_n: int, session_title: str, q: dict, idx: int, total: int) -> str:
    accent = ACCENTS[session_n]
    kicker = f"SESSION {session_n} &middot; KNOWLEDGE CHECK &middot; QUESTION {idx} of {total}"
    multi = q["multi"]
    correct = ",".join(q["correct"])
    rat = ""
    for o in q["options"]:
        if o["letter"] in q["correct"] and o.get("rationale"):
            rat = o["rationale"]
            break
    if not rat:
        for o in q["options"]:
            if o["letter"] not in q["correct"] and o.get("rationale"):
                rat = o["rationale"]
                break

    opts = "".join(
        f'<button class="sm-opt" data-ltr="{o["letter"]}" type="button">'
        f'<span class="sm-opt-l">{o["letter"]}</span>'
        f'<span class="sm-opt-t">{e(o["text"])}</span>'
        f'<span class="sm-opt-m"></span></button>'
        for o in q["options"]
    )
    submit = ('<div class="sm-check-submit"><button class="sm-submit" type="button" disabled>'
              'Submit</button></div>') if multi else ""
    hint = ('<span class="sm-check-hint">select all that apply</span>' if multi
            else '<span class="sm-check-hint">click an option</span>')

    by_letter = {o["letter"]: o["text"] for o in q["options"]}
    explanations = {o["letter"]: o.get("rationale", "") or "" for o in q["options"]}
    sources = q.get("sources", [])
    judge = {
        "prompt": q.get("prompt", ""),
        "options": [o["text"] for o in q["options"]],
        "answer": "; ".join(by_letter.get(l, "") for l in q["correct"]),
        "why": rat,
        "explanations": explanations,
        "sources": sources,
    }
    judge_attr = e(json.dumps(judge, ensure_ascii=False))
    sources_attr = e(json.dumps(sources, ensure_ascii=False))
    return (
        f'<div class="slide-native sm-skill sm-check" style="--accent:{accent};" '
        f'data-correct="{correct}" data-multi="{"1" if multi else ""}" '
        f'data-rationale="{e(rat)}" data-judge="{judge_attr}" data-sources="{sources_attr}">'
        f'<div class="kicker">{kicker}</div>'
        f'<h2>Check yourself {hint}</h2>'
        f'<p class="sm-check-q">{e(q["prompt"])}</p>'
        f'<div class="sm-opts">{opts}</div>'
        f'{submit}'
        f'<div class="sm-check-fb" style="display:none"></div>'
        f'<div class="sm-source"><i class="fa-solid fa-circle-question"></i> '
        f'Knowledge check &middot; Content Review Session {session_n}</div>'
        "</div>"
    )


def write(module: int, slides: list[dict]) -> str:
    os.makedirs(OUTDIR, exist_ok=True)
    jpath = os.path.join(OUTDIR, f"d{module}.json")
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(slides, f, indent=2, ensure_ascii=False)
        f.write("\n")
    compact = json.dumps(slides, ensure_ascii=False, separators=(", ", ": "))
    with open(os.path.join(OUTDIR, f"d{module}.js"), "w", encoding="utf-8") as f:
        f.write("window.DECK_DATA = window.DECK_DATA || {};\n")
        f.write(f'window.DECK_DATA["{module}"] = {compact};\n')
    return jpath


def build_session(session_n: int, title: str, questions: list[dict]) -> list[dict]:
    slides = []
    n = 1

    def add(native):
        nonlocal n
        slides.append({
            "n": n, "mode": "native", "native": native,
            "nativeClass": "", "image": "", "student": "",
            "instructor": "", "time": "", "audio": "",
        })
        n += 1

    add(divider_slide(session_n, title, len(questions)))
    total = len(questions)
    for idx, q in enumerate(questions, start=1):
        add(check_slide(session_n, title, q, idx, total))
    return slides


def main():
    total_slides = 0
    for n, (dirname, title) in SESSIONS.items():
        md_path = os.path.join(MD_DIR, dirname, CONTENT_REVIEW[n])
        questions = parse_session_markdown(md_path)
        slides = build_session(n, title, questions)
        write(n, slides)
        total_slides += len(slides)
        print(f"  d{n} ({title}): {len(slides)} slides = 1 divider + {len(questions)} questions")
    print(f"Built 5 Knowledge Check decks, {total_slides} slides total -> knowledgecheck/d1..d5.json")


if __name__ == "__main__":
    main()
