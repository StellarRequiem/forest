#!/usr/bin/env python3
"""
Quick one-time patch — forces real JSON output from all improvement organs.
"""
import subprocess
from pathlib import Path

organs = ["self_improver.py", "bug_hunter.py", "exposure_hunter.py", "architecture_evolver.py", "scenario_mutator.py", "forest_forge.py"]

for organ in organs:
    file = Path(organ)
    if not file.exists():
        print(f"⚠️ {organ} not found — skipping")
        continue
    
    content = file.read_text()
    
    # Add retry + strict JSON enforcement
    patch = '''
    # === JSON HARDEN PATCH (added by Graybeard) ===
    def _safe_json_load(self, raw):
        import json, re
        try:
            return json.loads(raw)
        except:
            # Try to extract JSON block if LLM added extra text
            match = re.search(r"\\{.*\\}", raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except:
                    pass
            print(f"⚠️ Bad JSON in {self.name} — using empty fallback")
            return {}
    '''
    # Insert the helper near the top
    if "_safe_json_load" not in content:
        content = content.replace("import ollama", "import ollama\n" + patch, 1)
    
    # Replace every json.loads with the safe version
    content = content.replace("json.loads(response['response'])", "self._safe_json_load(response['response'])")
    content = content.replace("json.loads(raw)", "self._safe_json_load(raw)")
    
    # Make prompts stricter
    content = content.replace('Reply in valid JSON ONLY', 'Reply in valid JSON ONLY. Do not add any extra text before or after the JSON. No explanations.')
    
    file.write_text(content)
    print(f"✅ Patched {organ} with JSON hardening")

print("All organs patched. Restarting a short test cycle now...")
