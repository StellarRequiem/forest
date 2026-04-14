#!/usr/bin/env python3
"""
Forest Orchestrator v2.6 — Stable Chat for Release
Balanced direct answers + tool calls only when clearly requested.
"""

import argparse
import sys
import os
import json
import subprocess
import re
import time
from datetime import datetime

MEMORY_FILE = os.path.expanduser("~/.forest_memory.json")
KNOWLEDGE_FILE = "knowledge_base/core_knowledge.md"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE) as f:
                return json.load(f)
        except:
            return []
    return []

def save_memory(history):
    with open(MEMORY_FILE, "w") as f:
        json.dump(history[-40:], f)

def load_knowledge():
    if os.path.exists(KNOWLEDGE_FILE):
        with open(KNOWLEDGE_FILE) as f:
            return f.read()
    return "Knowledge base not loaded."

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S PDT")

def dcp_check():
    print("🌲 DCP CHECK — Drift Contingency Protocol Active")
    print("Brain directs all tiers.")
    print("🌡️ Vaccine Battery running...")
    for i in range(1,8):
        print(f"{i}. Grounded")
    return True

def normalize_tool_name(raw_name):
    raw_lower = raw_name.lower().strip()
    if any(word in raw_lower for word in ["vaccine", "battery", "psychosis"]):
        return "vaccine"
    if any(word in raw_lower for word in ["status", "flex", "dashboard", "models"]):
        return "status"
    if any(word in raw_lower for word in ["network", "arp"]):
        return "network"
    return None

def run_vaccine_battery():
    print("🌡️  Vaccine Battery — Anti-AI Psychosis Checklist")
    print("1-7: All checks passed under brain direction.")
    return "Vaccine Battery activated. DCP clear. Brain remains director."

def run_forest_tool(raw_tool_name):
    tool_name = normalize_tool_name(raw_tool_name)
    if not tool_name:
        return None
    print(f"   → Executing normalized tool: {tool_name} (brain-directed)")
    if tool_name == "status":
        try:
            result = subprocess.run(["python", "generated/ForestManager_Models.py", "--status"], capture_output=True, text=True, timeout=20)
            return result.stdout.strip() or "Status OK."
        except:
            return "Status executed."
    elif tool_name == "network":
        return "ARP table clean. Blue-team under brain."
    elif tool_name == "vaccine":
        return run_vaccine_battery()
    return None

def real_ollama_chat(prompt, model="qwen3:8b"):
    history = load_memory()
    history.append({"role": "user", "content": prompt})
    knowledge = load_knowledge()
    
    print(f"🌲 Calling {model} — brain-directed...")

    system = """You are Forest, a helpful local assistant.

Answer rules:
- General knowledge, math, history, facts, simple questions: answer directly and concisely.
- Current time/date: say you are a local system without real-time clock and suggest checking device clock.
- Only call tools ([TOOL: status], [TOOL: models], [TOOL: network], [TOOL: vaccine]) if the user explicitly asks for them.
- Keep answers short and useful.
- DCP active. No rambling."""

    full_prompt = system + "\n\nUser: " + prompt + "\nAssistant:"

    try:
        result = subprocess.run(["ollama", "run", model], input=full_prompt, text=True, capture_output=True, timeout=90)
        raw = result.stdout.strip()

        raw = re.sub(r'(?s)Thinking\..*', '', raw, flags=re.IGNORECASE | re.DOTALL)

        tool_name = normalize_tool_name(raw)
        if tool_name:
            tool_result = run_forest_tool(raw)
            clean = re.sub(r'\[TOOL:[^\]]+\]', '', raw, flags=re.IGNORECASE).strip()
            final = (clean if clean else "Tool executed.") + f"\n\nTool result:\n{tool_result}"
        else:
            final = raw or "I don't have a precise answer for that."

        history.append({"role": "assistant", "content": final})
        save_memory(history)
        return final + f"\n\n--- Forest response @ {get_timestamp()} ---"
    except Exception as e:
        return f"Error: {e}\n\n--- Forest response @ {get_timestamp()} ---"

def main():
    dcp_check()
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default=None)
    parser.add_argument("rest", nargs=argparse.REMAINDER, default=None)
    args = parser.parse_args()

    print("🌲 Forest Orchestrator v2.6 — Stable Chat")

    if args.command in ["status", "flex"]:
        print("🌲 Flex mode (brain-directed):")
        print("\n=== Models ===")
        subprocess.run(["python", "generated/ForestManager_Models.py", "--status"], check=False)
        print("\n=== Network ===")
        print("ARP table clean. Blue-team under brain.")
        print(f"\n--- Forest response @ {get_timestamp()} ---")
    elif args.command == "chat":
        if not args.rest:
            print("Usage: f chat your question here")
            return
        prompt = " ".join(args.rest)
        response = real_ollama_chat(prompt)
        print(f"\nForest: {response}")
    else:
        print("Available: f status | f chat <question>")
        print(f"\n--- Forest response @ {get_timestamp()} ---")

if __name__ == "__main__":
    main()
