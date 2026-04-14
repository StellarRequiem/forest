#!/usr/bin/env python3
"""
Forest Mouth v2.0 — Realigned under CUS Brain
Output / communication layer. All output routed through brain.
"""

from forest_brain import log_chain

class ForestMouth:
    def speak(self, message):
        print(f"[MOUTH] {message}")
        log_chain("MOUTH_OUTPUT", message[:100])
        # In full system this would go through orchestrator for tool calls

print("=== Forest Mouth v2.0 Loaded — Brain Gated ===")
