# design_system_manager.py
# v4.1 - Clean manager for awesome-design-md integration
# Pulls real design rules (colors, buttons, spacing, etc.) so our AI stops guessing

import os
import subprocess
from pathlib import Path
from typing import Optional, Dict

class DesignSystemManager:
    def __init__(self, base_dir: str = "."):
        self.design_dir = Path(base_dir) / "design-systems"
        self.design_dir.mkdir(exist_ok=True)
        self.active_system: Optional[str] = None
        self.last_loaded: Optional[str] = None

    def fetch(self, brand: str) -> bool:
        """Download the DESIGN.md for a brand (Spotify, Apple, Ollama, etc.)"""
        brand = brand.lower().replace(" ", "-").replace(".", "-")
        target_dir = self.design_dir / brand
        target_dir.mkdir(exist_ok=True)

        url = f"https://raw.githubusercontent.com/VoltAgent/awesome-design-md/main/design-md/{brand}/DESIGN.md"
        
        try:
            subprocess.run(["curl", "-s", "-o", str(target_dir / "DESIGN.md"), url], check=True)
            print(f"✅ Successfully downloaded design system: {brand}")
            self.active_system = brand
            self.last_loaded = str(target_dir / "DESIGN.md")
            return True
        except Exception as e:
            print(f"❌ Failed to download {brand}. Error: {e}")
            return False

    def load(self, brand: str) -> Optional[str]:
        """Read the DESIGN.md file and return its content"""
        path = self.design_dir / brand.lower().replace(" ", "-").replace(".", "-") / "DESIGN.md"
        if path.exists():
            content = path.read_text(encoding="utf-8")
            self.active_system = brand
            self.last_loaded = str(path)
            return content
        print(f"⚠️ Design system {brand} not found. Run fetch first.")
        return None

    def get_injection_prompt(self, brand: str) -> str:
        """Returns the full design rules so the AI must follow them exactly"""
        content = self.load(brand)
        if not content:
            return f"// WARNING: Design system '{brand}' not found. Falling back to generic styling."

        return f"""=== STRICT DESIGN SYSTEM: {brand.upper()} ===
You MUST follow EVERY rule in this DESIGN.md for colors, typography, spacing, buttons, cards, inputs, and layout.
Do not invent your own styles. Use the exact names and values from this file.

{content}

AGENT PROMPT GUIDE (from the original DESIGN.md):
- Use exact semantic color names and hex values
- Follow the exact typography hierarchy and spacing scale
- Build components (buttons, cards, inputs) exactly as described, including hover/active/disabled states
- Respect all do’s and don’ts
- Make it responsive exactly as specified
"""
    
    def get_status(self) -> Dict:
        """Show what design system is currently active"""
        return {
            "active_system": self.active_system,
            "last_loaded": self.last_loaded,
            "design_dir": str(self.design_dir)
        }
