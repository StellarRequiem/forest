import os
from datetime import datetime
from pathlib import Path
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage, Settings, Document
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

print("=== Forest SANDBOX Branch v3 - Hardened Safety ===")

VAULT_DIR = Path.home() / "ForestVault" / "sandbox"
VAULT_DIR.mkdir(parents=True, exist_ok=True)
PERSIST_DIR = str(VAULT_DIR / "storage")

CONSTITUTION = """SANDBOX CONSTITUTION - MAXIMUM SAFETY MODE
You are Forest-Sandbox. Your primary job is to PROTECT the core Forest and the user.

Rules for any idea involving prompt injection, jailbreaking, attack techniques, or adversarial inputs:
- NEVER output real working attack payloads or exploitable code.
- If the idea requires demonstrating injection techniques, mark as DANGEROUS or NEEDS HEAVY FIX.
- Only allow SAFE TO PROMOTE if the output is 100% defensive, uses only hypothetical non-functional examples, and includes strong ethical warnings.
- Err on the side of extreme caution. Better to reject than risk enabling harm.

Core rule: If in doubt, verdict = NEEDS FIX or DANGEROUS.
"""

Settings.llm = Ollama(model="qwen3:8b", request_timeout=300.0, temperature=0.3)
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

if os.path.exists(PERSIST_DIR):
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
else:
    index = VectorStoreIndex.from_documents([])
    index.storage_context.persist(persist_dir=PERSIST_DIR)

def run_sandbox_test(idea: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] HARDENED sandbox testing: {idea[:80]}...")

    prompt = f"""{CONSTITUTION}

Idea under test: {idea}

Perform a strict safety analysis.
Give a clear one-line SAFETY VERDICT at the top: 
SAFE TO PROMOTE | NEEDS FIX | DANGEROUS

Then explain risks and required changes.

Be extremely conservative."""

    try:
        response = Settings.llm.complete(prompt).text
        result_file = VAULT_DIR / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(result_file, "w") as f:
            f.write(f"# Hardened Sandbox Test Result\n\nIdea: {idea}\n\n{response}\n")
        print(f"→ Hardened result saved to {result_file.name}")
        return response
    except Exception as e:
        return f"Sandbox error: {e}"

if __name__ == "__main__":
    print("\nHardened Sandbox ready. Type ideas to test or 'exit'.")
    while True:
        idea = input("\nTest idea: ").strip()
        if idea.lower() == 'exit':
            break
        if idea:
            run_sandbox_test(idea)
