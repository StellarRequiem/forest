# worker_code_generator.py
# v5.3 — Robust LLM Code Generator (forces clean HTML only)

from pathlib import Path
from typing import Dict, Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
import re

try:
    from design_system_manager import DesignSystemManager
    from meta_harness_runner import MetaHarnessRunner
except ImportError:
    class DesignSystemManager: 
        def get_injection_prompt(self, brand): return "// Design system not loaded"
    class MetaHarnessRunner:
        def log_step(self, *args, **kwargs): pass

class CodeGenerationWorker:
    def __init__(self):
        self.design_manager = DesignSystemManager()
        self.meta = MetaHarnessRunner()
        self.output_dir = Path("generated_output")
        self.output_dir.mkdir(exist_ok=True)
        self.llm = ChatOllama(model="phi3:mini", temperature=0.2)

    def generate(self, research_summary: str, target: str, design_brand: Optional[str] = None) -> Dict:
        self.meta.log_step("Worker: Code Generation", target, f"Design: {design_brand or 'none'}")

        design_prompt = self.design_manager.get_injection_prompt(design_brand) if design_brand else ""

        system_prompt = f"""You are an expert frontend engineer in the Forest swarm.
You MUST output **ONLY** clean, complete, valid HTML + Tailwind CSS.
No explanations, no refusals, no markdown, no extra text.
Use the exact design rules below."""

        user_prompt = f"""RESEARCH GOAL: {target}

DESIGN RULES (follow exactly):
{design_prompt}

Generate a complete single-file HTML page for the target above.
Use Tailwind via CDN. Make it beautiful, responsive, and on-brand."""

        try:
            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            raw = response.content.strip()

            # Force clean HTML extraction
            html_match = re.search(r'<!DOCTYPE html>.*</html>', raw, re.DOTALL | re.IGNORECASE)
            clean_html = html_match.group(0) if html_match else raw

        except Exception as e:
            clean_html = f"<!-- Generation failed: {e} -->\n<h1>{target}</h1>"

        filename = f"{target.replace(' ', '_').replace(':', '')}.html"
        filepath = self.output_dir / filename
        filepath.write_text(clean_html, encoding="utf-8")

        result = {
            "status": "success",
            "files_created": [str(filepath)],
            "message": f"✅ Clean LLM-generated {filename} (design: {design_brand or 'none'})",
            "location": str(self.output_dir)
        }

        self.meta.log_step("Worker Complete", target, result["message"], success=True)
        return result

# Global singleton
code_worker = CodeGenerationWorker()
