#!/usr/bin/env python3
"""
🌲 Forest Blue-Team Dashboard v1.1 — Updated for Training Pipeline
"""
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import json
from datetime import datetime

class ForestDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("🌲 Forest Blue-Team Guardian v1.1 — Mac Mini Edition")
        self.root.geometry("1100x720")
        self.root.configure(bg="#1e1e1e")

        ttk.Label(root, text="Forest Home Network Guardian + Training Pipeline", 
                  font=("Helvetica", 18, "bold"), background="#1e1e1e", foreground="#22c55e").pack(pady=10)

        # Tool buttons
        tools = [
            ("Network Dashboard", ["tools/network_dashboard.py"]),
            ("ARP Monitor (v2)", ["tools/arp_monitor.py"]),
            ("Update Privacy Hosts", ["tools/privacy_hosts.py"]),
            ("Harden Firewall (v3.3)", ["tools/firewall_harden.py"]),
            ("Model Manager", ["tools/model_manager.py", "--status"]),
            ("Phishing Trainer", ["ui/phishing_trainer.py"]),
            ("Docker Guard", ["tools/docker_guard.py"]),
        ]

        for label, cmd in tools:
            btn = ttk.Button(root, text=label, command=lambda c=cmd: self.run_tool(c))
            btn.pack(pady=4, padx=40, fill="x")

        # Status panel
        self.status_text = tk.Text(root, height=18, bg="#2d2d2d", fg="#a0a0a0", font=("Consolas", 10))
        self.status_text.pack(pady=10, padx=40, fill="both", expand=True)

        ttk.Button(root, text="Refresh Status", command=self.refresh_status).pack(pady=8)

        self.refresh_status()

    def run_tool(self, cmd_list):
        try:
            subprocess.Popen(["python3"] + [os.path.expanduser("~/forest-blue-team-guardian/" + c) for c in cmd_list])
            messagebox.showinfo("Launched", f"Started {' '.join(cmd_list)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_status(self):
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, f"🌲 Forest Dashboard @ {datetime.now()}\n")
        self.status_text.insert(tk.END, "="*60 + "\n\n")

        # Show last training improvements
        try:
            with open("training_improvements.log", "r") as f:
                lines = f.readlines()[-15:]
            self.status_text.insert(tk.END, "Latest Training Improvements (with critic scores):\n")
            for line in lines:
                self.status_text.insert(tk.END, line)
        except:
            self.status_text.insert(tk.END, "No training improvements logged yet.\n")

        self.status_text.insert(tk.END, "\nFirewall anchor status: Check with 'sudo pfctl -a forest/blue -s rules'\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ForestDashboard(root)
    root.mainloop()
