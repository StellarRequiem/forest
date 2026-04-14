#!/usr/bin/env python3
"""
🌲 Forest Claude Integrator (Anthropic)
Requires: pip install anthropic
"""
import os
import sys
from datetime import datetime
import argparse

try:
    import anthropic
except ImportError:
    print("❌ anthropic package not found.")
    print("   Run: pip install anthropic")
    sys.exit(1)

def get_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️ ANTHROPIC_API_KEY not set.")
        print("   Create ~/.forest_env with: export ANTHROPIC_API_KEY=sk-ant-...")
        print("   Then run: source ~/.forest_env")
        return None
    return anthropic.Anthropic(api_key=api_key)

def chat(prompt, model="claude-3-5-sonnet-20241022"):
    client = get_client()
    if not client:
        return
    print(f"🌲 Calling Claude ({model}) @ {datetime.now()}")
    try:
        message = client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        response = message.content[0].text
        print("\n=== Claude Response ===")
        print(response)
    except Exception as e:
        print(f"Claude error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", nargs="?", default="Hello from Forest. Tell me how you can help integrate open-source models.")
    parser.add_argument("--model", default="claude-3-5-sonnet-20241022")
    args = parser.parse_args()
    
    # Load env file if it exists
    env_file = os.path.expanduser("~/.forest_env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, val = line.strip().split("=", 1)
                    os.environ[key.strip()] = val.strip()
    
    chat(args.prompt, args.model)
