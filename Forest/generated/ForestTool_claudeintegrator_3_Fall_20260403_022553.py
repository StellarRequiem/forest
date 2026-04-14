#!/usr/bin/env python3
"""
🌲 Forest Claude Integrator (Anthropic API wrapper)
Secure, local-first proxy for Claude 3.5 Sonnet / Opus / 4
"""
import os
import anthropic
from datetime import datetime
import argparse

def get_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️ ANTHROPIC_API_KEY not found in environment.")
        print("   Create ~/.forest_env and add: export ANTHROPIC_API_KEY=sk-...")
        return None
    return anthropic.Anthropic(api_key=api_key)

def chat_with_claude(prompt, model="claude-3-5-sonnet-20241022", max_tokens=2048):
    client = get_client()
    if not client:
        return "API key missing. Check ~/.forest_env"
    
    print(f"🌲 Calling Claude ({model}) @ {datetime.now()}")
    try:
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        response = message.content[0].text
        print("\n=== Claude Response ===")
        print(response)
        return response
    except Exception as e:
        print(f"Claude API error: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", nargs="?", default="Hello Claude, introduce yourself briefly.", help="Prompt to send to Claude")
    parser.add_argument("--model", default="claude-3-5-sonnet-20241022", help="Model to use")
    args = parser.parse_args()
    
    # Load env if exists
    env_file = os.path.expanduser("~/.forest_env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, val = line.strip().split("=", 1)
                    os.environ[key.strip()] = val.strip()
    
    chat_with_claude(args.prompt, args.model)
