from pathlib import Path
import json

proposed = Path.home() / "ForestVault" / "proposed_questions.json"
bank = Path.home() / "ForestVault" / "question_bank.json"

if proposed.exists():
    with open(proposed) as f:
        data = json.load(f)
    print(f"Sanitizing {len(data)} proposed questions...")
    for q in data:
        if "scenario" in q and "email" not in q:
            q["email"] = q["scenario"]
        if "correct_answer" in q and "correct" not in q:
            q["correct"] = q["correct_answer"]
        # Safety filter: force defensive language
        if "feedback_correct" in q:
            q["feedback_correct"] = q["feedback_correct"].replace("No", "Yes - This is Phishing").replace("Low", "High")
    with open(proposed, "w") as f:
        json.dump(data, f, indent=2)
    print("Safety gate applied to proposed questions.")

print("Safety gate complete.")
