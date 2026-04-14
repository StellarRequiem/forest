import tkinter as tk
import subprocess
from tkinter import ttk

class TrainerLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Forest Blue Team Trainer Suite")
        self.root.geometry("880x720")          # wider and balanced
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(True, True)        # allow resizing

        # Title
        tk.Label(self.root, text="FOREST", font=("Helvetica", 44, "bold"), bg="#0a0a0a", fg="#22c55e").pack(pady=(40, 10))
        tk.Label(self.root, text="Blue Team Trainer Suite", font=("Helvetica", 16), bg="#0a0a0a", fg="#aaaaaa").pack(pady=(0, 30))

        # Scrollable area with better fill
        main_frame = tk.Frame(self.root, bg="#0a0a0a")
        main_frame.pack(fill="both", expand=True, padx=60, pady=10)

        self.canvas = tk.Canvas(main_frame, bg="#0a0a0a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#0a0a0a")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Smooth scrolling (mouse wheel + trackpad)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Tools - wider buttons, better spacing
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
            btn = tk.Button(self.scrollable_frame, text=name,
                            command=lambda s=script: subprocess.Popen(["python", s]),
                            font=("Helvetica", 13, "bold"),
                            bg="#1f1f1f", fg="#e0e0e0",
                            activebackground="#2a2a2a", activeforeground="#22c55e",
                            relief="flat", bd=0, width=52, height=2)   # wider buttons
            btn.pack(pady=8, padx=10)   # balanced padding

            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2a2a2a"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1f1f1f"))

        # Footer
        tk.Label(self.root, text="All sessions logged to ~/ForestVault/ • Hash chain protected",
                 font=("Helvetica", 10), bg="#0a0a0a", fg="#555555").pack(pady=25)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 25)), "units")   # smoother on macOS

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainerLauncher(root)
    root.mainloop()
