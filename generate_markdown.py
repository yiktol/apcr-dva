"""
Generate markdown files for each question from extracted data.
"""

import json
from pathlib import Path


def generate_question_title(question_text: str) -> str:
    """Generate a short title from the question text."""
    # Take first sentence or first 80 chars
    first_sentence = question_text.split(".")[0]
    if len(first_sentence) > 80:
        first_sentence = first_sentence[:77] + "..."
    return first_sentence


def generate_markdown(question: dict, session_num: int, q_num: int) -> str:
    """Generate markdown content for a single question."""
    title = generate_question_title(question["question"])
    correct_letters = question["correct_letters"]
    options = question["options"]

    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(question["question"])
    lines.append("")

    # List all options
    for letter in sorted(options.keys()):
        opt = options[letter]
        opt_text = opt["text"] if opt["text"] else opt["explanation"][:100]
        lines.append(f"- {letter}) {opt_text}")
    lines.append("")

    # Answer section
    lines.append("## Answer")
    lines.append("")
    correct_str = ", ".join(correct_letters)
    lines.append(f"**{correct_str}**")
    lines.append("")

    for letter in correct_letters:
        if letter in options:
            opt = options[letter]
            opt_text = opt["text"] if opt["text"] else ""
            lines.append(f"- **{letter}) {opt_text}**")
            # Break explanation into bullet points
            explanation = opt["explanation"]
            bullets = _split_explanation(explanation)
            for bullet in bullets:
                lines.append(f"  - {bullet}")
            lines.append("")

    # Why other options are incorrect
    lines.append("## Why the other options are incorrect")
    lines.append("")

    incorrect_letters = sorted([k for k in options if k not in correct_letters])
    for letter in incorrect_letters:
        opt = options[letter]
        opt_text = opt["text"] if opt["text"] else ""
        lines.append(f"- **{letter}) {opt_text}**")
        explanation = opt["explanation"]
        bullets = _split_explanation(explanation)
        for bullet in bullets:
            lines.append(f"  - {bullet}")
        lines.append("")

    return "\n".join(lines)


def _split_explanation(explanation: str) -> list[str]:
    """Split a long explanation into digestible bullet points."""
    if not explanation:
        return ["No explanation provided"]

    # Split on sentence boundaries
    sentences = []
    current = ""
    for char in explanation:
        current += char
        if char in ".!" and len(current) > 20:
            sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())

    # Group into reasonable bullet points (max 3-4)
    if len(sentences) <= 4:
        return [s for s in sentences if s]

    # Combine short sentences
    bullets = []
    combined = ""
    for s in sentences:
        if len(combined) + len(s) < 150:
            combined += " " + s if combined else s
        else:
            if combined:
                bullets.append(combined)
            combined = s
    if combined:
        bullets.append(combined)

    return bullets[:4] if bullets else [explanation[:200]]


def generate_all_markdown():
    """Generate markdown files for all sessions."""
    with open("extracted_questions.json") as f:
        sessions = json.load(f)

    for session_num_str, questions in sessions.items():
        session_num = int(session_num_str)
        print(f"\nSession {session_num}: generating {len(questions)} markdown files")

        for q in questions:
            q_num = q["number"]
            q_dir = Path(f"session{session_num}/exam-strategy/q{q_num}")
            q_dir.mkdir(parents=True, exist_ok=True)

            md_content = generate_markdown(q, session_num, q_num)
            md_path = q_dir / f"q{q_num}.md"
            md_path.write_text(md_content)
            print(f"  Created: {md_path}")


if __name__ == "__main__":
    generate_all_markdown()
