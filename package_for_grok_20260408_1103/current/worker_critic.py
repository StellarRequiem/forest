# worker_critic.py
# v5.3 — Bulletproof Critic (no more "Critic failed")

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
import json
import re

class CriticWorker:
    def __init__(self):
        self.llm = ChatOllama(model="phi3:mini", temperature=0.0)

    def critique(self, generated_code: str, target: str, design_brand: str = None):
        system = """You are a ruthless senior frontend critic.
Score 0-100 on:
- Exact Ollama design system adherence
- Clean code / best practices
- Accessibility & responsiveness

Reply with **ONLY** this exact JSON (no extra text):
{"score": 85, "issues": ["short list of problems"], "suggested_fix": "one-sentence suggestion"}"""

        prompt = f"Target: {target}\nDesign: {design_brand or 'none'}\n\nCode to critique:\n{generated_code[:3500]}"

        try:
            response = self.llm.invoke([
                SystemMessage(content=system),
                HumanMessage(content=prompt)
            ])
            text = response.content.strip()

            # Super robust JSON extraction
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                data = json.loads(match.group(0))
            else:
                data = {"score": 60, "issues": ["JSON parse failed"], "suggested_fix": ""}

            return {
                "score": int(data.get("score", 60)),
                "issues": data.get("issues", []),
                "suggested_fix": data.get("suggested_fix", "")
            }
        except Exception as e:
            return {"score": 55, "issues": [f"Critic error: {str(e)[:60]}"], "suggested_fix": ""}

critic = CriticWorker()
