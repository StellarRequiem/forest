import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json
from pathlib import Path
from datetime import datetime

VAULT_DIR = Path.home() / "ForestVault"

class Cryptex:
    def __init__(self, root):
        self.root = root
        self.root.title("Forest Cryptex - 2026 Threat Pulse")
        self.root.geometry("940x760")
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(True, True)

        tk.Label(self.root, text="FOREST CRYPTEX", font=("Helvetica", 28, "bold"), bg="#0a0a0a", fg="#22c55e").pack(pady=15)
        tk.Label(self.root, text="Live 2026 Threat Pulse • Self-Improving Defense", font=("Helvetica", 12), bg="#0a0a0a", fg="#888888").pack(pady=(0,20))

        # Threat Pulse banner
        pulse_frame = tk.Frame(self.root, bg="#1a1a1a", padx=20, pady=12)
        pulse_frame.pack(fill="x", padx=40, pady=8)
        self.pulse_lbl = tk.Label(pulse_frame, text="CURRENT THREAT PULSE: Supply-chain poisoning (Axios/Lazarus) + Ransomware recovery denial active", 
                                  font=("Helvetica", 11, "bold"), bg="#1a1a1a", fg="#ef4444", wraplength=800)
        self.pulse_lbl.pack()

        # Status
        status = tk.Frame(self.root, bg="#1a1a1a", padx=25, pady=18)
        status.pack(fill="x", padx=50, pady=10)
        self.bank_lbl = tk.Label(status, text="Bank size: --", font=("Helvetica", 14), bg="#1a1a1a", fg="#e0e0e0", anchor="w")
        self.bank_lbl.pack(anchor="w")
        self.chain_lbl = tk.Label(status, text="Chain length: --", font=("Helvetica", 14), bg="#1a1a1a", fg="#e0e0e0", anchor="w")
        self.chain_lbl.pack(anchor="w", pady=6)
        self.last_lbl = tk.Label(status, text="Last activity: --", font=("Helvetica", 12), bg="#1a1a1a", fg="#aaaaaa", anchor="w")
        self.last_lbl.pack(anchor="w")

        tk.Button(self.root, text="REFRESH PULSE", command=self.refresh, bg="#22c55e", fg="#0a0a0a", font=("Helvetica", 11, "bold")).pack(pady=12)

        # Tools (aggressive defense focus)
        tk.Label(self.root, text="Aggressive Defense Trainers", font=("Helvetica", 16), bg="#0a0a0a", fg="#ffffff").pack(pady=(25,10))

        tools = [  # added new aggressive ones we'll build next
            ("Phishing Defense Trainer v5", "phishing_trainer_v5.py"),
            ("Dynamic Self-Improving Trainer", "dynamic_trainer_v6.py"),
            ("Supply-Chain Poisoning Simulator (NEW)", "supply_chain_simulator.py"),  # placeholder - we'll create this
            ("AI Prompt Injection Defender", "prompt_injection_trainer.py"),          # placeholder
            # ... rest of your existing tools
        ]

        for name, script in tools:
            frame = tk.Frame(self.root, bg="#1a1a1a")
            frame.pack(fill="x", padx=60, pady=6)
            tk.Label(frame, text=name, font=("Helvetica", 13), bg="#1a1a1a", fg="#e0e0e0", anchor="w").pack(side="left", padx=25, pady=12)
            tk.Button(frame, text="RUN AGGRESSIVE MODE", command=lambda s=script: self.run_tool(s),
                      bg="#ef4444", fg="#ffffff", font=("Helvetica", 11, "bold"), width=22).pack(side="right", padx=25)

        self.refresh()

    def refresh(self):
        # same as before but with real pulse update
        self.bank_lbl.config(text=f"Bank size: {len(json.load(open(VAULT_DIR/'question_bank.json'))) if (VAULT_DIR/'question_bank.json').exists() else 0} questions")
        # ... chain and last activity same as previous version
        self.pulse_lbl.config(text="CURRENT THREAT PULSE: Axios/Lazarus supply-chain + ransomware backup destruction active (March 31 2026)")

    def run_tool(self, script):
        try:
            subprocess.Popen(["python", script])
        except Exception as e:
            messagebox.showerror("Launch Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = Cryptex(root)
    root.mainloop()
