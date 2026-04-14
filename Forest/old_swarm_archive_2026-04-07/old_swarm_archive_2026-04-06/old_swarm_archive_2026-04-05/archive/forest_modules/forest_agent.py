import os
import time
import json
import threading
from datetime import datetime
from pathlib import Path
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage, Settings, Document
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

print("=== Forest Agent starting - Persistent RAG Thinker ===")

VAULT_DIR = Path.home() / "ForestVault"
VAULT_DIR.mkdir(exist_ok=True)
PERSIST_DIR = str(VAULT_DIR / "storage")
IDEAS_DIR = VAULT_DIR / "ideas"
IDEAS_DIR.mkdir(exist_ok=True)

CONSTITUTION = """REFUSAL-FIRST CONSTITUTION v1.0
You are Forest. Continuously analyze blue-team trainer data.
Suggest concrete improvements to existing trainers.
Stay defensive only. Never offensive tools.
"""

Settings.llm = Ollama(model="qwen3:8b", request_timeout=180.0, temperature=0.4)
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

# Persistent RAG index
if os.path.exists(PERSIST_DIR):
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
else:
    index = VectorStoreIndex.from_documents([])
    index.storage_context.persist(persist_dir=PERSIST_DIR)

thinking = True
stop_event = threading.Event()

def load_all_trainer_data():
    data = []
    for f in VAULT_DIR.glob("*.json"):
        try:
            with open(f) as fp:
                content = json.load(fp)
                data.append({"file": f.name, "content": content})
        except:
            pass
    return data

def background_thinker():
    global thinking
    while not stop_event.is_set():
        if not thinking:
            time.sleep(10)
            continue

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Forest thinking... analyzing vault")
        data = load_all_trainer_data()

        if data:
            summary = f"{len(data)} session files found. Latest: {data[-1]['file'] if data else 'none'}"
            prompt = f"""Analyze the trainer data below and suggest ONE concrete improvement for the next version of the trainer suite.
Data summary: {summary}

Be specific: more scenarios, better feedback, new UI element, new metric, etc.
Output only the improvement idea and the exact code change needed."""

            try:
                response = Settings.llm.complete(prompt).text
                idea_file = IDEAS_DIR / f"idea_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                with open(idea_file, "w") as f:
                    f.write(f"# Forest Idea {datetime.now()}\n\n{response}\n\n")
                print(f"→ New idea saved to {idea_file.name}")
            except Exception as e:
                print(f"Thinking error: {e}")

        time.sleep(90)  # think every 90 seconds (adjustable)

# Start background thinker thread
thinker_thread = threading.Thread(target=background_thinker, daemon=True)
thinker_thread.start()

print("\nForest Agent is ONLINE and thinking.")
print("Commands:")
print("  'idle'     → pause thinking")
print("  'think'    → resume thinking")
print("  'status'   → show current mode")
print("  'exit'     → shut down agent\n")

while True:
    try:
        cmd = input("Forest> ").strip().lower()
        if cmd == "exit":
            stop_event.set()
            print("Shutting down Forest Agent...")
            break
        elif cmd == "idle":
            thinking = False
            print("Forest now in IDLE mode (background thinking paused)")
        elif cmd == "think":
            thinking = True
            print("Forest resumed thinking")
        elif cmd == "status":
            print(f"Current mode: {'THINKING (RAG active)' if thinking else 'IDLE'}")
        else:
            print("Unknown command. Use: idle | think | status | exit")
    except KeyboardInterrupt:
        stop_event.set()
        break

print("Forest Agent stopped.")
# --- Safe manual import handler (add this at the bottom before the while loop) ---

def import_external_data():
    import_dir = VAULT_DIR / "import"
    imported = 0
    for file in import_dir.glob("*.txt") + import_dir.glob("*.md") + import_dir.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
            doc = Document(text=f"Imported external idea from {file.name}:\n{content[:2000]}...")
            index.insert(doc)
            index.storage_context.persist(persist_dir=PERSIST_DIR)
            imported += 1
            print(f"✓ Imported: {file.name}")
        except Exception as e:
            print(f"Failed to import {file.name}: {e}")
    if imported > 0:
        print(f"Imported {imported} external files into RAG vault.")
    else:
        print("No new files in ~/ForestVault/import/ to import.")

# Call this when you type "import"
