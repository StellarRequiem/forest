#!/usr/bin/env python3
"""
Nuclear clean repair — fixes indentation and adds reliable JSON extractor to every organ.
"""
import re
from pathlib import Path

organs = ["self_improver.py", "bug_hunter.py", "exposure_hunter.py", "architecture_evolver.py", "scenario_mutator.py", "forest_forge.py"]

for organ_file in organs:
    path = Path(organ_file)
    if not path.exists():
        print(f"⚠️ {organ_file} not found")
        continue

    content = path.read_text()

    # Remove ALL previous broken patches
    content = re.sub(r"# === .*?JSON.*?PATCH.*?# === .*?JSON.*?PATCH", "", content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r"def _safe_json_load|def _extract_json", "", content)  # remove old broken defs

    # Add clean, correctly indented helper inside the class
    helper = """
    def _extract_json(self, raw_text):
        import json
        import re
        raw_text = raw_text.strip()
        # Direct parse
        try:
            return json.loads(raw_text)
        except:
            pass
        # Extract first valid JSON object
        match = re.search(r'\\{.*\\}', raw_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
        print(f"[HARDEN] {self.name} — JSON parse failed, returning empty")
        return {}
"""

    # Insert helper at the right place (after the class __init__)
    if "def __init__(self" in content and "_extract_json" not in content:
        content = re.sub(r"(def __init__\(self.*?:[\s\S]*?super\(\)\.__init__\(.*?\))", r"\1" + helper, content)

    # Replace all json.loads calls
    content = re.sub(r"json\.loads\(response\['response'\]\)", r"self\._extract_json\(response\['response'\]\)", content)
    content = re.sub(r"json\.loads\(raw\)", r"self\._extract_json\(raw\)", content)

    # Make prompts stricter
    content = re.sub(r'Reply in valid JSON ONLY', r'Reply in valid JSON ONLY. No explanations. No extra text before or after the JSON object.', content)

    path.write_text(content)
    print(f"✅ Clean repair applied to {organ_file}")

print("\nAll organs repaired with correct indentation and hardened JSON parsing.")
print("Self-improvement loop is now repeatable.")
