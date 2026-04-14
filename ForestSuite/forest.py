import os
import subprocess
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage, Settings, Document
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

print("=== Forest Self-Improving Loop Engine v3.2 - Timed + Hash Chain ===")

VAULT_DIR = Path.home() / "ForestVault"
VAULT_DIR.mkdir(exist_ok=True)
CHAIN_LOG = VAULT_DIR / "training_chain.json"

Settings.llm = Ollama(model="qwen3:8b", request_timeout=300.0, temperature=0.4)
hot_llm = Ollama(model="qwen3:8b", request_timeout=360.0, temperature=0.7)
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

def get_last_hash():
    if CHAIN_LOG.exists():
        try:
            with open(CHAIN_LOG) as f:
                chain = json.load(f)
            return chain[-1]["hash"] if chain else "0"
        except:
            return "0"
    return "0"

def append_to_chain(entry_type, details):
    last_hash = get_last_hash()
    timestamp = datetime.now().isoformat()
    data_str = f"{timestamp}|{entry_type}|{json.dumps(details, sort_keys=True)}|{last_hash}"
    current_hash = hashlib.sha256(data_str.encode()).hexdigest()

    entry = {
        "timestamp": timestamp,
        "type": entry_type,
        "details": details,
        "previous_hash": last_hash,
        "hash": current_hash
    }

    if CHAIN_LOG.exists():
        with open(CHAIN_LOG) as f:
            chain = json.load(f)
    else:
        chain = []
    chain.append(entry)
    with open(CHAIN_LOG, "w") as f:
        json.dump(chain, f, indent=2)

    print(f"Chain entry: {entry_type} @ {timestamp[:19]} | Hash: {current_hash[:12]}...")

def check_drift():
    if not CHAIN_LOG.exists():
        return
    with open(CHAIN_LOG) as f:
        chain = json.load(f)
    valid = True
    for i in range(1, len(chain)):
        prev_hash = chain[i-1]["hash"]
        data_str = f"{chain[i]['timestamp']}|{chain[i]['type']}|{json.dumps(chain[i]['details'], sort_keys=True)}|{prev_hash}"
        if hashlib.sha256(data_str.encode()).hexdigest() != chain[i]["hash"]:
            print("DRIFT DETECTED!")
            valid = False
            break
    if valid:
        print(f"Chain OK ({len(chain)} entries). No drift.")

def run_auto_test():
    print("Running one auto-run cycle...")
    subprocess.run(["python", "dynamic_trainer_v6.py", "--auto"], check=True)
    append_to_chain("AUTO_RUN_CYCLE", {"status": "completed"})

def compile_adaptive_material():
    print("Compiling adaptive material from real results...")
    dynamic_log = VAULT_DIR / "dynamic_sessions.json"
    if not dynamic_log.exists():
        return
    with open(dynamic_log) as f:
        history = json.load(f)
    avg_acc = sum(s.get("percentage", 0) for s in history) / len(history) if history else 0
    prompt = f"""Generate 8 new adaptive phishing scenarios based on average accuracy {avg_acc:.1f}%.
Output ONLY valid JSON array with keys: email, correct, feedback_correct, feedback_incorrect, tier"""
    try:
        response = hot_llm.complete(prompt).text
        new_q = json.loads(response)
        proposed = VAULT_DIR / "proposed_questions.json"
        with open(proposed, "w") as f:
            json.dump(new_q, f, indent=2)
        append_to_chain("COMPILE_MATERIAL", {"new_questions": len(new_q)})
        print(f"Compiled {len(new_q)} new adaptive questions.")
    except Exception as e:
        print(f"Compile failed: {e}")

def import_proposed():
    proposed = VAULT_DIR / "proposed_questions.json"
    bank = VAULT_DIR / "question_bank.json"
    if not proposed.exists():
        return
    with open(proposed) as f:
        new_q = json.load(f)
    if bank.exists():
        with open(bank) as f:
            current = json.load(f)
    else:
        current = []
    current.extend(new_q)
    with open(bank, "w") as f:
        json.dump(current, f, indent=2)
    append_to_chain("IMPORT_PROPOSED", {"imported": len(new_q), "bank_size": len(current)})
    print(f"Imported {len(new_q)} questions. Bank now {len(current)}.")

def self_improve_loop(minutes):
    end_time = time.time() + (minutes * 60)
    cycle = 0
    print(f"Starting self-improving loop for {minutes} minutes...")
    while time.time() < end_time:
        cycle += 1
        remaining = int((end_time - time.time()) / 60)
        print(f"\n=== Self-Improve Cycle {cycle} | {remaining} min left ===")
        run_auto_test()
        compile_adaptive_material()
        import_proposed()
        check_drift()
        time.sleep(10)  # short pause between full cycles
    print("Timed self-improving loop completed.")

def chat():
    print("\nForest commands:")
    print("  auto run [N]          → Run N manual cycles")
    print("  self improve [MIN]    → Run continuous self-improving loop for MIN minutes")
    print("  compile material      → Generate new adaptive questions")
    print("  import                → Add proposed questions to bank")
    print("  bank size             → Show current bank size")
    print("  chain status          → Show hash chain")
    print("  check drift           → Verify chain integrity")
    print("  exit")

    while True:
        cmd = input("\nForest> ").strip()
        if cmd.lower() == "exit":
            print("Forest shutting down.")
            break
        elif cmd.startswith("self improve"):
            try:
                minutes = int(cmd.split()[-1])
            except:
                minutes = 30
            self_improve_loop(minutes)
        elif cmd.startswith("auto run"):
            try:
                cycles = int(cmd.split()[-1])
            except:
                cycles = 1
            for _ in range(cycles):
                run_auto_test()
        elif "compile" in cmd.lower():
            compile_adaptive_material()
        elif cmd.lower() == "import":
            import_proposed()
        elif "bank size" in cmd.lower():
            bank = VAULT_DIR / "question_bank.json"
            if bank.exists():
                with open(bank) as f:
                    data = json.load(f)
                print(f"Current question bank size: {len(data)}")
            else:
                print("Bank not found.")
        elif "chain status" in cmd.lower():
            if CHAIN_LOG.exists():
                with open(CHAIN_LOG) as f:
                    chain = json.load(f)
                print(f"Chain length: {len(chain)} entries")
                if chain:
                    print(f"Latest: {chain[-1]['timestamp'][:19]} | {chain[-1]['type']}")
            else:
                print("No chain yet.")
        elif "check drift" in cmd.lower():
            check_drift()
        else:
            print("Unknown command.")

if __name__ == "__main__":
    chat()
