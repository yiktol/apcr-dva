"""
Master build script: Extracts questions, generates timer, markdown, diagrams, and PPTX.
Run this single script to build all exam strategy materials from scratch.
"""

import sys
import time
from pathlib import Path

print("=" * 60)
print("AWS DVA-C02 Exam Strategy Materials Generator")
print("=" * 60)

# Step 1: Extract questions
print("\n[1/5] Extracting questions from Answer Key documents...")
from extract_questions import extract_all_sessions
import json

sessions = extract_all_sessions()

# Save extracted data
output = {}
for session_num, questions in sessions.items():
    output[str(session_num)] = questions
    print(f"  Session {session_num}: {len(questions)} questions extracted")

with open("extracted_questions.json", "w") as f:
    json.dump(output, f, indent=2)

total_questions = sum(len(q) for q in sessions.values())
print(f"  Total: {total_questions} questions saved to extracted_questions.json")

# Step 2: Generate countdown timer
print("\n[2/5] Generating countdown timer GIFs...")
from generate_timer import create_countdown_gif

for session_num in range(1, 6):
    output_dir = Path(f"session{session_num}/exam-strategy")
    output_dir.mkdir(parents=True, exist_ok=True)
    gif_path = output_dir / "countdown_2min.gif"
    create_countdown_gif(str(gif_path))

# Step 3: Generate markdown files
print("\n[3/5] Generating markdown files...")
from generate_markdown import generate_all_markdown
generate_all_markdown()

# Step 4: Generate architecture diagrams
print("\n[4/5] Generating architecture diagrams...")
from generate_diagrams import generate_all_diagrams
generate_all_diagrams()

# Step 5: Generate PowerPoint presentations
print("\n[5/5] Generating PowerPoint presentations...")
from generate_pptx import generate_all_pptx
generate_all_pptx()

# Summary
print("\n" + "=" * 60)
print("BUILD COMPLETE")
print("=" * 60)
print(f"\nGenerated materials for {total_questions} questions across 5 sessions:")
for session_num, questions in sessions.items():
    print(f"  Session {session_num}: {len(questions)} questions")
    for q in questions:
        q_dir = Path(f"session{session_num}/exam-strategy/q{q['number']}")
        print(f"    q{q['number']}/: md + diagrams + pptx")

print("\nOutput structure:")
print("  session{N}/exam-strategy/")
print("  ├── countdown_2min.gif")
print("  └── q{N}/")
print("      ├── q{N}.md")
print("      ├── option_a.png ... option_d.png")
print("      ├── q{N}_exam_strategy.pptx")
print("      └── create_diagrams.py")
