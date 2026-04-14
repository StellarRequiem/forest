import os
import subprocess
try:
    import ollama
    USE_CLIENT = True
except ImportError:
    USE_CLIENT = False

class CUSCore:
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")   # force 8B
        print(f"[CUS Core] Ready - Using model: {self.model} | Client: {'ollama-py' if USE_CLIENT else 'subprocess'}")

    def _call_llm(self, prompt: str) -> str:
        print(f"[LLM Call] Prompt length: {len(prompt)} chars | First 80: {prompt[:80]}...")

        if USE_CLIENT:
            try:
                import ollama
                resp = ollama.generate(model=self.model, prompt=prompt, options={"temperature": 0.1})
                return resp['response'].strip()
            except:
                pass

        try:
            result = subprocess.run(["ollama", "run", self.model, prompt], 
                                  capture_output=True, text=True, timeout=90)
            return result.stdout.strip() if result.returncode == 0 else f"[Ollama Error] {result.stderr.strip()}"
        except Exception as e:
            return f"[LLM Failed] {str(e)}"

    def process_proposal(self, proposal: str) -> str:
        print(f"[CUS] === Processing: {proposal[:100]}... ===")
        return f"[Generic response for: {proposal[:200]}]"

if __name__ == "__main__":
    c = CUSCore()
    print(c.process_proposal("test"))
