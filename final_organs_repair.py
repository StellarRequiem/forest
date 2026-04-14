#!/usr/bin/env python3
"""
FINAL CLEAN REPAIR — fixes indentation and adds reliable JSON handling.
"""
import re
from pathlib import Path

organs = ["self_improver.py", "bug_hunter.py", "exposure_hunter.py", 
          "architecture_evolver.py", "scenario_mutator.py", "forest_forge.py"]

for organ_file in organs:
    path = Path(organ_file)
    if not path.exists():
        print(f"⚠️ {organ_file} not found")
        continue

    content = path.read_text()

    # Remove any old broken patches
    content = re.sub(r"# ===.*?JSON.*?PATCH.*?# ===.*?JSON.*?PATCH", "", content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r"def _safe_json_load|def _extract_json", "", content, flags=re.IGNORECASE)

    # Add clean helper with correct 4-space indentation
        import json
        import re
        raw_text = raw_text.strip()
        try:
            return json.loads(raw_text)
        except:
            pass
        match = re.search(r'\\{.*\\}', raw_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
        print("[HARDEN] JSON parse failed — returning empty")
        return {}
"""

    # Insert helper after __init__
    if "def __init__(self" in content and "_extract_json" not in content:
        content = re.sub(r"(def __init__\(self.*?:[\s\S]*?super\(\)\.__init__\(.*?\))", r"\1" + helper, content)

    # Replace json.loads calls
    content = re.sub(r"json\.loads\(response\['response'\]\)", r"_extract_json(response['response'])", content)
    content = re.sub(r"json\.loads\(raw\)", r"_extract_json(raw)", content)

    # Stricter prompt
    content = re.sub(r'Reply in valid JSON ONLY', r'Reply in valid JSON ONLY. No explanations. No extra text before or after the JSON object.', content)

    path.write_text(content)
    print(f"✅ Final clean repair applied to {organ_file}")

print("\nAll organs repaired with correct indentation.")
print("Self-improvement loop is now repeatable.")
