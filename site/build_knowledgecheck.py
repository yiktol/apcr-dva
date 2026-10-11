#!/usr/bin/env python3
"""
Build the per-session Knowledge Check decks for knowledgecheck.html by
parsing the five Exam Strategy "Answer Key" markdown files under ../md and
emitting one slide-array bundle per session (knowledgecheck/d<N>.{json,js}),
in the same dual-emit shape as site/build_decks.py and the reference
aib-c01/build_knowledgecheck.py.

Source files (one per session):
    ../md/session1/02 - APCR-DVA - Exam Strategy Session 1 - Answer Key.md
    ../md/session2/03 - APCR-DVA - Exam Strategy Session 2 - Answer Key.md
    ../md/session3/04 - APCR-DVA - Exam Strategy Session 3 - Answer Key.md
    ../md/session4/05 - APCR-DVA - Exam Strategy Session 4 - Answer Key.md
    ../md/session5/06 - APCR-DVA - Exam Strategy Session 5 - Answer Key.md

Each file is a sequence of "## <heading>" question blocks. The heading style
is NOT consistent across (or even within) files -- session 2 alone uses three
different styles ("## 1)", "## Q4:", and a bare "## 5 <title>") -- so the
heading regex is deliberately permissive: QUESTION_HEADING_RE matches an
optional "Q", digits, and an optional ":"/")" separator, keeping the rest of
the line as the stem.

Within a block, the correct/incorrect answer markup appears in one of four
observed shapes ("formats"), detected in this order (first match wins):

  Format C   -- named-service, letter-in-parens: "The correct answer(s)
               are:" / "The incorrect answer(s) are:" followed by paragraphs
               like "**Amazon API Gateway (B)**: explanation...". Option text
               is the bolded service name; letter comes from the parens.
               (session1 Q1, Q5 variant with plain "A." dot-letter paragraphs)

  Format B   -- inline-stated correct answer: "The correct answer is
               **C: text**" (or just "**A**:" with no inline text), plus an
               "incorrect options are:" paragraph list "A. text: expl" or
               "A) text - expl". (session1 Q2, Q3, Q6)

  Format D   -- bare letter-paren option paragraphs "A) text", correctness
               shown by bold-wrapping the whole correct paragraph and/or an
               inline "Correct"/"Incorrect" word. No "correct answer is"
               lead-in sentence. (session2 Q1, Q2)

  Format A   -- colon-letter (or paren-letter) option paragraphs: "A:
               Incorrect. ..." / "D: **Correct**. ..." where the rationale
               sentence doubles as the option text (there is no separate,
               shorter option label). Falls back to "A-positional" when NO
               letter markers are present at all but 2+ paragraphs each
               begin with "Correct."/"Incorrect." -- letters are then
               assigned A, B, C... in document order. (session1 Q4; session2
               Q4 colon-letter, Q5 positional; session3 Q1-4 colon-letter,
               Q5 paren-letter; session4 and session5, all colon-letter)

A paragraph that does not start with a new letter marker (and is not a
"The correct/incorrect answer(s)..." marker line) is treated as a
continuation of the PREVIOUS option's rationale -- this is how trailing
"For more information about X, see Y." footer sentences attach to the
option that precedes them, in every format.

Known source quirks (kept as-is, not "fixed"):
  - Session 1 Q2 and Q3 are verbatim duplicate questions in the source; both
    are emitted as separate questions (no de-duplication).
  - Session 2's heading styles are inconsistent ("## 1)"/"## 2)" for Q1/Q2,
    "## Q4:" for Q4, a bare "## 5 Amazon RDS..." for Q5 -- Q3 does not exist
    in the source at all, so session 2 has only 4 questions.
  - Session 5's source has only 5 questions (Q1-Q5); there is no "Q6".

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
    1: ("session1", "02 - APCR-DVA - Exam Strategy Session 1 - Answer Key.md",
        "Infrastructure Foundations"),
    2: ("session2", "03 - APCR-DVA - Exam Strategy Session 2 - Answer Key.md",
        "Development with AWS Services"),
    3: ("session3", "04 - APCR-DVA - Exam Strategy Session 3 - Answer Key.md",
        "Decoupling, Caching, Auth & Observability"),
    4: ("session4", "05 - APCR-DVA - Exam Strategy Session 4 - Answer Key.md",
        "Testing and Deployment"),
    5: ("session5", "06 - APCR-DVA - Exam Strategy Session 5 - Answer Key.md",
        "Security, AI Security & Observability"),
}

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

# Matches "## 1:", "## Q4:", "## 1)", "## #5", "## 5 Amazon RDS...".
QUESTION_HEADING_RE = re.compile(r"^##\s*#?[Qq]?\s*(\d+)\s*[:).]?\s*(.*)$")

BOLD_LINE_RE = re.compile(r"^\*\*(.+)\*\*$")

WORD_COUNTS = {"TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}


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

def split_questions(text: str):
    """Split a session's markdown body into (heading_text, block_lines)
    tuples, one per '## ...' question heading, in document order."""
    lines = text.split("\n")
    heading_idxs = []
    for i, line in enumerate(lines):
        m = QUESTION_HEADING_RE.match(line)
        if m:
            heading_idxs.append((i, m))

    blocks = []
    for idx, (line_i, m) in enumerate(heading_idxs):
        heading_text = m.group(2).strip()
        block_start = line_i + 1
        block_end = heading_idxs[idx + 1][0] if idx + 1 < len(heading_idxs) else len(lines)
        block_lines = lines[block_start:block_end]
        blocks.append((heading_text, block_lines))
    return blocks


def assemble_stem(heading_text: str, block_lines: list[str]) -> tuple[str, list[str]]:
    """Combine the heading text with any immediately-following standalone
    bold prompt line(s) (e.g. extra scenario context lines plus "**Which
    solution...(SELECT THREE)**") into the final question stem. Several
    source blocks (session1 Q1, Q5) have more than one such bold line in a
    row before the first non-bold paragraph; all of them are appended in
    order. Returns (stem, remaining_lines_after_the_prompt)."""
    stem = heading_text
    rest = block_lines
    i = 0
    while i < len(rest) and rest[i].strip() == "":
        i += 1
    while i < len(rest):
        candidate = rest[i].strip()
        if candidate == "":
            i += 1
            continue
        m = BOLD_LINE_RE.match(candidate)
        if not m:
            break
        inner = m.group(1).strip()
        # A bold line that is itself an answer/option paragraph (starts with
        # a letter marker, or with "Correct."/"Incorrect.") is NOT part of
        # the stem -- stop absorbing before it (session2 Q5's sole option
        # paragraph is fully bold-wrapped and would otherwise be eaten).
        if re.match(r"^([A-G])[.):]\s", inner) or re.match(r"^(Correct|Incorrect)\.", inner):
            break
        stem = f"{stem} {inner}".strip()
        i += 1
    rest = rest[i:]
    return stem, rest


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


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------

CORRECT_ARE_RE = re.compile(r"[Tt]he correct answers? are")
INCORRECT_ARE_RE = re.compile(r"[Tt]he incorrect answers?( is| are)?:?")
CORRECT_IS_BOLD_RE = re.compile(r"[Tt]he correct answer is\s*\*\*")
SERVICE_PAREN_RE = re.compile(r"\*\*([^*(]+?)\s*\(([A-G])\)\*\*\s*:?\s*(.*)$")
BARE_LETTER_PAREN_RE = re.compile(r"^([A-G])\)\s+(.+)$")
BARE_LETTER_COLON_RE = re.compile(r"^([A-G])\*{0,2}\s*[:)]\s*(.*)$")
CORRECT_WORD_RE = re.compile(r"^Correct\.?\s*(.*)$", re.DOTALL)
INCORRECT_WORD_RE = re.compile(r"^Incorrect\.?\s*(.*)$", re.DOTALL)


def detect_format(block_text: str, paras: list[str]) -> str:
    if CORRECT_ARE_RE.search(block_text) and SERVICE_PAREN_RE.search(block_text):
        return "C"
    # Format C-variant: "The correct answers are **A, C, and E**:" headline
    # (a bolded letter list, no per-option parens) followed by plain
    # "A. text - rationale" paragraphs.
    if CORRECT_ARE_RE.search(block_text) and re.search(r"are\s*\*\*[A-G](,\s*[A-G])*,?\s*(and\s*[A-G])?\*\*", block_text):
        return "C"
    if CORRECT_IS_BOLD_RE.search(block_text):
        return "B"
    # Format D: bare "A) text" paragraphs with no "correct answer is" lead-in.
    letter_paren_paras = [p for p in paras if BARE_LETTER_PAREN_RE.match(p.strip())]
    if len(letter_paren_paras) >= 2:
        return "D"
    # Format A (colon/paren letter options with inline Correct./Incorrect.)
    lettered = [p for p in paras if BARE_LETTER_COLON_RE.match(p.strip())]
    if lettered:
        return "A"
    # Format A-positional: no letters at all, but Correct./Incorrect. markers.
    marked = [p for p in paras if re.match(r"^\**\s*(Correct|Incorrect)\.", p.strip())]
    if len(marked) >= 2:
        return "A-positional"
    return "A"


# ---------------------------------------------------------------------------
# Per-format extraction -> list of {"letter","text","rationale","correct":bool}
# ---------------------------------------------------------------------------

def extract_format_c(stem: str, paras: list[str]):
    # Split paragraphs into "correct" vs "incorrect" sections on the marker
    # lines, then pull every "**Service (Letter)**: rationale" paragraph.
    correct_letters = []
    options = {}
    order = []
    section = None
    for p in paras:
        if CORRECT_ARE_RE.match(p) or re.match(r"^The correct answers? are", p):
            section = "correct"
            # "The correct answers are **A, C, and E**:" - no per-option text
            # here, just the headline; letters (if present) recorded below.
            m = re.search(r"are\s*\*\*([^*]+)\*\*", p)
            if m:
                for l in re.findall(r"[A-G]", m.group(1)):
                    if l not in correct_letters:
                        correct_letters.append(l)
            continue
        if INCORRECT_ARE_RE.match(p) or re.match(r"^The incorrect answers? (is|are)", p):
            section = "incorrect"
            continue
        m = SERVICE_PAREN_RE.search(p)
        if m:
            name, letter, rest = m.group(1).strip(), m.group(2), m.group(3).strip()
            if letter not in options:
                options[letter] = {"letter": letter, "text": name, "rationale": rest}
                order.append(letter)
            else:
                options[letter]["rationale"] = (options[letter]["rationale"] + " " + rest).strip()
            if section == "correct" and letter not in correct_letters:
                correct_letters.append(letter)
            continue
        # Plain "A. text - rationale" paragraph (Q5 variant: no bold wrap).
        m2 = re.match(r"^([A-G])\.\s*(.+)$", p)
        if m2:
            letter, rest = m2.group(1), m2.group(2).strip()
            text, rationale = split_dash(rest)
            if letter not in options:
                options[letter] = {"letter": letter, "text": text, "rationale": rationale}
                order.append(letter)
            else:
                options[letter]["rationale"] = (options[letter]["rationale"] + " " + rest).strip()
            continue
        # Continuation paragraph: attach to the most recently seen option.
        if order:
            last = order[-1]
            options[last]["rationale"] = (options[last]["rationale"] + " " + p).strip()

    order_sorted = sorted(order)
    opts = [options[l] for l in order_sorted]
    for o in opts:
        o["correct"] = o["letter"] in correct_letters

    # Sanity check the stated SELECT count against the number of correct
    # letters found; warn (not raise) on mismatch.
    m = re.search(r"[Ss]elect\s+(\w+)", stem)
    if m and m.group(1).upper() in WORD_COUNTS:
        expected = WORD_COUNTS[m.group(1).upper()]
        if expected != len(correct_letters):
            print(f"    warning: stem says SELECT {m.group(1)} ({expected}) but "
                  f"found {len(correct_letters)} correct letters: {correct_letters}",
                  file=sys.stderr)
    return opts


def split_dash(rest: str) -> tuple[str, str]:
    """Split 'option text - rationale' on the first ' - '; else no rationale."""
    if " - " in rest:
        text, rationale = rest.split(" - ", 1)
        return text.strip(), rationale.strip()
    return rest.strip(), ""


def split_colon(rest: str) -> tuple[str, str]:
    """Split 'option text: rationale' on the first ': '; else no rationale."""
    if ": " in rest:
        text, rationale = rest.split(": ", 1)
        return text.strip(), rationale.strip()
    return rest.strip(), ""


def extract_format_b(paras: list[str]):
    options = {}
    order = []
    correct_letter = None
    correct_inline_text = ""
    marker_idx = None

    for i, p in enumerate(paras):
        m = re.search(r"[Tt]he correct answer is\s*\*\*([A-G])\s*[:.)]?\s*(.*?)\*\*", p)
        if m:
            correct_letter = m.group(1)
            correct_inline_text = m.group(2).strip()
            marker_idx = i
            break

    for i, p in enumerate(paras):
        if i == marker_idx:
            continue
        if re.match(r"^[Tt]he incorrect (options|answers?)( is| are)?:?\s*$", p.strip()):
            continue
        mo = re.match(r"^([A-G])[.):]\s*(.+)$", p.strip())
        if mo:
            letter, rest = mo.group(1), mo.group(2).strip()
            text, rationale = split_dash(rest)
            if ":" in text and not rationale:
                text2, rationale2 = split_colon(rest)
                text, rationale = text2, rationale2
            if letter not in options:
                options[letter] = {"letter": letter, "text": text, "rationale": rationale}
                order.append(letter)
            else:
                options[letter]["rationale"] = (options[letter]["rationale"] + " " + rest).strip()
            continue
        if order:
            last = order[-1]
            options[last]["rationale"] = (options[last]["rationale"] + " " + p).strip()

    if correct_letter is not None:
        if correct_letter not in options:
            options[correct_letter] = {"letter": correct_letter, "text": correct_inline_text, "rationale": ""}
            order.insert(0, correct_letter)
        elif correct_inline_text:
            # Inline text from "The correct answer is **C: text**" wins.
            options[correct_letter]["text"] = correct_inline_text

    order.sort()
    opts = [options[l] for l in order]
    for o in opts:
        o["correct"] = o["letter"] == correct_letter
    return opts


def extract_format_d(paras: list[str]):
    options = {}
    order = []
    for p in paras:
        p = p.strip()
        is_bold_wrapped = p.startswith("**") and p.endswith("**")
        probe = strip_bold(p) if is_bold_wrapped else p
        m = BARE_LETTER_PAREN_RE.match(probe)
        if not m:
            if order:
                last = order[-1]
                options[last]["rationale"] = (options[last]["rationale"] + " " + p).strip()
            continue
        letter, rest = m.group(1), m.group(2).strip()
        correct = is_bold_wrapped or bool(re.search(r"\bCorrect\b", rest)) and not re.search(r"\bIncorrect\b", rest)
        # Text vs rationale: split at the first sentence boundary that
        # precedes a standalone "Incorrect"/"Correct" marker word; else the
        # whole remainder is both text and rationale (no explicit marker).
        mm = re.search(r"\b(Incorrect|Correct)\b\.?\s*(.*)$", rest)
        if mm and mm.start() > 0:
            text = rest[:mm.start()].strip().rstrip(".")
            rationale = (mm.group(2) or "").strip()
        else:
            text = rest
            rationale = rest
        options[letter] = {"letter": letter, "text": text, "rationale": rationale, "correct": correct}
        order.append(letter)
    return [options[l] for l in order]


def extract_format_a(paras: list[str]):
    options = {}
    order = []
    for p in paras:
        p = p.strip()
        probe = p[2:] if p.startswith("**") else p
        m = BARE_LETTER_COLON_RE.match(probe)
        if not m:
            if order:
                last = order[-1]
                options[last]["rationale"] = (options[last]["rationale"] + " " + p).strip()
                options[last]["text"] = options[last]["rationale"]
            continue
        letter, rest = m.group(1), m.group(2).strip()
        rest = strip_bold_prefix_run(rest)
        correct = False
        cm = CORRECT_WORD_RE.match(rest)
        im = INCORRECT_WORD_RE.match(rest)
        if cm:
            correct = True
            rest = cm.group(1).strip()
        elif im:
            correct = False
            rest = im.group(1).strip()
        rest = rest.lstrip(".").strip()
        options[letter] = {"letter": letter, "text": rest, "rationale": rest, "correct": correct}
        order.append(letter)
    return [options[l] for l in order]


def strip_bold_prefix_run(rest: str) -> str:
    """Bolding placement around the Correct./Incorrect. marker varies: the
    whole sentence may be bold ('**D: Correct**. ...' already had its 'D:'
    letter prefix consumed by the caller), just the word may be bold
    ('A: **Correct.** text'), or the bold run may exclude the trailing
    period ('**A: Correct**. text'). Since Format A never uses bold for
    anything other than marking Correct/Incorrect, it is safe to strip ALL
    '**' markers from the remainder up front so CORRECT_WORD_RE/
    INCORRECT_WORD_RE can match a plain leading 'Correct'/'Incorrect'."""
    return rest.replace("**", "")


def extract_format_a_positional(paras: list[str]):
    options = []
    idx = 0
    for p in paras:
        p = p.strip().replace("**", "")
        cm = CORRECT_WORD_RE.match(p)
        im = INCORRECT_WORD_RE.match(p)
        if cm or im:
            correct = bool(cm)
            rest = (cm or im).group(1).strip()
            letter = LETTERS[idx]
            idx += 1
            options.append({"letter": letter, "text": rest, "rationale": rest, "correct": correct})
            continue
        # Continuation paragraph (e.g. "For more information..." footer).
        if options:
            options[-1]["rationale"] = (options[-1]["rationale"] + " " + p).strip()
    return options


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def parse_block(heading_text: str, block_lines: list[str]) -> dict:
    stem, rest_lines = assemble_stem(heading_text, block_lines)
    paras = paragraphs_of(rest_lines)
    block_text = "\n".join(rest_lines)

    fmt = detect_format(block_text, paras)
    if fmt == "C":
        opts = extract_format_c(stem, paras)
    elif fmt == "B":
        opts = extract_format_b(paras)
    elif fmt == "D":
        opts = extract_format_d(paras)
    elif fmt == "A-positional":
        opts = extract_format_a_positional(paras)
    else:
        opts = extract_format_a(paras)

    correct = [o["letter"] for o in opts if o.get("correct")]
    options = [{"letter": o["letter"], "text": o["text"], "rationale": o.get("rationale", "")} for o in opts]
    return {
        "prompt": stem,
        "options": options,
        "correct": correct,
        "multi": len(correct) > 1,
        "format": fmt,
    }


def parse_session_markdown(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    questions = []
    for heading_text, block_lines in split_questions(text):
        q = parse_block(heading_text, block_lines)
        if q["options"] and q["correct"]:
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
    judge = {
        "prompt": q.get("prompt", ""),
        "options": [o["text"] for o in q["options"]],
        "answer": "; ".join(by_letter.get(l, "") for l in q["correct"]),
        "why": rat,
        "explanations": explanations,
    }
    judge_attr = e(json.dumps(judge, ensure_ascii=False))
    return (
        f'<div class="slide-native sm-skill sm-check" style="--accent:{accent};" '
        f'data-correct="{correct}" data-multi="{"1" if multi else ""}" '
        f'data-rationale="{e(rat)}" data-judge="{judge_attr}">'
        f'<div class="kicker">{kicker}</div>'
        f'<h2>Check yourself {hint}</h2>'
        f'<p class="sm-check-q">{e(q["prompt"])}</p>'
        f'<div class="sm-opts">{opts}</div>'
        f'{submit}'
        f'<div class="sm-check-fb" style="display:none"></div>'
        f'<div class="sm-source"><i class="fa-solid fa-circle-question"></i> '
        f'Knowledge check &middot; Exam Strategy Session {session_n} Answer Key</div>'
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
    for n, (dirname, filename, title) in SESSIONS.items():
        md_path = os.path.join(MD_DIR, dirname, filename)
        questions = parse_session_markdown(md_path)
        slides = build_session(n, title, questions)
        write(n, slides)
        total_slides += len(slides)
        note = "  (note: Q2 and Q3 are duplicate questions in the source)" if n == 1 else ""
        print(f"  d{n} ({title}): {len(slides)} slides = 1 divider + {len(questions)} questions{note}")
    print(f"Built 5 Knowledge Check decks, {total_slides} slides total -> knowledgecheck/d1..d5.json")


if __name__ == "__main__":
    main()
