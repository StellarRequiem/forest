import os
from datetime import datetime
from pathlib import Path
from llama_index.llms.ollama import Ollama

print("=== Sandbox Question Proposal Tool ===")

VAULT_DIR = Path.home() / "ForestVault"
PROPOSAL_FILE = VAULT_DIR / "proposed_questions.json"

llm = Ollama(model="qwen3:8b", request_timeout=180.0, temperature=0.6)

def propose_new_questions(count=5):
    prompt = f"""Generate {count} new, high-quality, realistic phishing or social engineering scenarios for a blue-team trainer.
Each scenario must have:
- A clear email/SMS/voice/website description
- Correct answer ("Yes" or "No")
- Strong feedback_correct and feedback_incorrect

Make them varied and educational. Output as valid JSON array."""

    try:
        response = llm.complete(prompt).text
        # Extract JSON (simple parsing for now)
        import json
        questions = json.loads(response)
        with open(PROPOSAL_FILE, "w") as f:
            json.dump(questions, f, indent=2)
        print(f"Proposed {len(questions)} new questions saved to {PROPOSAL_FILE}")
        return questions
    except Exception as e:
        print(f"Proposal failed: {e}")
        return []

if __name__ == "__main__":
    propose_new_questions()
