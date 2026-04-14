import tkinter as tk
import subprocess
from tkinter import ttk

class TrainerLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Forest Blue Team Trainer Suite")
        self.root.geometry("860x720")
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(False, False)

        # Title
        tk.Label(self.root, text="FOREST", font=("Helvetica", 48, "bold"), bg="#0a0a0a", fg="#22c55e").pack(pady=(40, 5))
        tk.Label(self.root, text="Blue Team Trainer Suite", font=("Helvetica", 16), bg="#0a0a0a", fg="#aaaaaa").pack(pady=(0, 30))

        # Scrollable area
        canvas = tk.Canvas(self.root, bg="#0a0a0a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0a0a0a")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=50, pady=20)
        scrollbar.pack(side="right", fill="y", padx=(0, 40))

        # Tool list
        tools = [
            ("Phishing Defense Trainer v5", "phishing_trainer_v5.py"),
            ("URL Risk Scanner Trainer", "url_risk_scanner_trainer.py"),
            ("Dynamic Self-Improving Trainer", "dynamic_trainer_v6.py"),
            ("Password Hygiene Trainer", "password_hygiene_trainer.py"),
            ("Network Log Analyzer Trainer", "network_log_analyzer_trainer.py"),
            ("DNS Risk Analyzer Trainer", "dns_risk_analyzer_trainer.py"),
            ("File Integrity Trainer", "file_integrity_trainer.py"),
            ("Incident Response Simulator", "incident_response_trainer.py"),
            ("Red Team Simulation Trainer", "red_team_simulation_trainer.py"),
            ("Email Header Analyzer", "email_header_analyzer_trainer.py"),
        ]

        for name, script in tools:
            btn = tk.Button(scrollable_frame, text=name, command=lambda s=script: subprocess.Popen(["python", s]),
                            font=("Helvetica", 13, "bold"),
                            bg="#1f1f1f", fg="#e0e0e0",
                            activebackground="#2a2a2a", activeforeground="#22c55e",
                            relief="flat", bd=0, width=50, height=2)
            btn.pack(pady=10, padx=20)

            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2a2a2a"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1f1f1f"))

        # Footer
        tk.Label(self.root, text="All sessions logged to ~/ForestVault/ • Hash chain protected", 
                 font=("Helvetica", 10), bg="#0a0a0a", fg="#555555").pack(pady=30)

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainerLauncher(root)
    root.mainloop()
