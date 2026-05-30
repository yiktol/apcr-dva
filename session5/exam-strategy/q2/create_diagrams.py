"""Auto-generated script to regenerate diagrams for Session 5 Q2."""
import sys
sys.path.insert(0, "/home/ubuntu/apcr-dva")
from generate_diagrams import generate_diagrams_for_question
import json

with open("/home/ubuntu/apcr-dva/extracted_questions.json") as f:
    sessions = json.load(f)

question = sessions["5"][1]
generate_diagrams_for_question(question, 5, 2)
print("Done!")
