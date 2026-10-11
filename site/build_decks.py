#!/usr/bin/env python3
"""
Build the per-session slide deck data bundles for deck.html from the
converted session markdown files in ../md.

For each session 1..5 writes:
    decks/m<N>.js    -> window.DECK_DATA["<N>"] = [ {n, mode, image, title,
                        hidden, student}, ... ]
    decks/m<N>.json  -> same payload (HTTP fetch fallback)

Each markdown file (one per session) uses this per-slide block format:

    ## Slide N — <title>              (hidden slides append ' _(hidden)_')
    ![Slide N](images/slide-NN.png)
    ### Notes
    <one or more paragraphs, blank-line separated, or literal '_No speaker
    notes._'>
    ---

Images are copied from md/session<N>/images/slide-NN.png into
decks/images/session<N>/slide-NN.png so site/ is self-contained and
portable, and the deck JSON/JS reference the resulting relative path
(relative to site/, i.e. "decks/images/session<N>/slide-NN.png").

Slide object shape:
    { "n": int, "mode": "image", "image": str, "title": str,
      "hidden": bool, "student": str }

No LLM or server is needed; deck.html renders this data client-side.

Usage:  python3 build_decks.py   (run from the site/ directory, or anywhere
        -- paths are resolved relative to this script's location)
"""
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
MD_DIR = os.path.join(HERE, "..", "md")
DECKS_DIR = os.path.join(HERE, "decks")
IMAGES_DIR = os.path.join(DECKS_DIR, "images")

SESSIONS = {
    1: ("session1", "02 - APCR-DVA - Content Review Session 1.md"),
    2: ("session2", "03 - APCR-DVA - Content Review Session 2.md"),
    3: ("session3", "04 - APCR-DVA - Content Review Session 3.md"),
    4: ("session4", "05 - APCR-DVA - Content Review Session 4.md"),
    5: ("session5", "06 - APCR-DVA - Content Review Session 5.md"),
}

SLIDE_HEADING_RE = re.compile(r"^## Slide (\d+) \u2014 (.*)$")
HIDDEN_SUFFIX_RE = re.compile(r"\s*:?\s*_\(hidden\)_\s*$")
NO_NOTES_LITERAL = "_No speaker notes._"

# Slides whose title matches this are the practice-question blocks
# ("Question 1: ...", etc.) and are excluded from the published decks.
QUESTION_TITLE_RE = re.compile(r"^Question\s+\d+\b", re.IGNORECASE)


def _is_excluded(slide):
    """A slide is dropped from the published deck if it is a hidden slide
    (facilitator-only) or a practice-question slide."""
    return slide["hidden"] or bool(QUESTION_TITLE_RE.match(slide["title"]))


def parse_session(session_num, dirname, filename):
    """Parse one session's markdown file into a list of slide dicts."""
    md_path = os.path.join(MD_DIR, dirname, filename)
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")

    # Find the line index of every slide heading, then slice the text into
    # per-slide blocks (from one heading up to the next heading, or EOF).
    heading_idxs = []
    for i, line in enumerate(lines):
        m = SLIDE_HEADING_RE.match(line)
        if m:
            heading_idxs.append((i, m))

    slides = []
    for idx, (line_i, m) in enumerate(heading_idxs):
        n = int(m.group(1))
        raw_title = m.group(2)
        hidden = bool(HIDDEN_SUFFIX_RE.search(raw_title))
        title = HIDDEN_SUFFIX_RE.sub("", raw_title).strip()

        block_start = line_i + 1
        block_end = heading_idxs[idx + 1][0] if idx + 1 < len(heading_idxs) else len(lines)
        block = lines[block_start:block_end]

        student = _extract_notes(block)
        image = f"decks/images/{dirname}/slide-{n:02d}.png"

        slides.append({
            "n": n,
            "mode": "image",
            "image": image,
            "title": title,
            "hidden": hidden,
            "student": student,
        })

    return slides


def _extract_notes(block_lines):
    """Within a slide's block, pull the paragraphs under '### Notes' up to
    the next '---' line (or end of block). Returns plain text with
    paragraphs joined by '\n', or '' if there are no notes."""
    try:
        notes_i = next(i for i, l in enumerate(block_lines) if l.strip() == "### Notes")
    except StopIteration:
        return ""

    notes_lines = []
    for l in block_lines[notes_i + 1:]:
        if l.strip() == "---":
            break
        notes_lines.append(l)

    notes_text = "\n".join(notes_lines).strip()
    if not notes_text or notes_text == NO_NOTES_LITERAL:
        return ""

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", notes_text)]
    paragraphs = [p for p in paragraphs if p and p != NO_NOTES_LITERAL]
    return "\n".join(paragraphs)


def _copy_images(session_num, dirname, slides):
    """Copy each slide's source image into decks/images/<dirname>/, verifying
    it exists first. Idempotent (shutil.copy2 overwrites cleanly)."""
    src_dir = os.path.join(MD_DIR, dirname, "images")
    dest_dir = os.path.join(IMAGES_DIR, dirname)
    os.makedirs(dest_dir, exist_ok=True)
    for s in slides:
        basename = f"slide-{s['n']:02d}.png"
        src = os.path.join(src_dir, basename)
        if not os.path.exists(src):
            raise FileNotFoundError(f"missing source image: {src}")
        dest = os.path.join(dest_dir, basename)
        shutil.copy2(src, dest)


def main():
    os.makedirs(DECKS_DIR, exist_ok=True)

    totals = {}
    for n, (dirname, filename) in SESSIONS.items():
        all_slides = parse_session(n, dirname, filename)

        # Exclude facilitator-only hidden slides and practice-question slides
        # from the published deck.
        kept = [s for s in all_slides if not _is_excluded(s)]
        dropped = len(all_slides) - len(kept)

        _copy_images(n, dirname, kept)

        with open(os.path.join(DECKS_DIR, f"m{n}.json"), "w", encoding="utf-8") as f:
            json.dump(kept, f, indent=2, ensure_ascii=False)
            f.write("\n")

        compact = json.dumps(kept, ensure_ascii=False, separators=(", ", ": "))
        with open(os.path.join(DECKS_DIR, f"m{n}.js"), "w", encoding="utf-8") as f:
            f.write("window.DECK_DATA = window.DECK_DATA || {};\n")
            f.write(f'window.DECK_DATA["{n}"] = {compact};\n')

        totals[n] = (len(kept), dropped)

    print("Built session decks:")
    total_slides = 0
    for n, (count, dropped) in totals.items():
        print(f"  m{n}: {count} slides ({dropped} removed: hidden + question) -> decks/m{n}.js")
        total_slides += count
    print("Total:", total_slides)


if __name__ == "__main__":
    main()
