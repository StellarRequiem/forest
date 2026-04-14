import tkinter as tk
from tkinter import messagebox
import datetime
import json
import random
from pathlib import Path

VAULT_LOG = Path.home() / "ForestVault" / "email_header_sessions.json"
VAULT_LOG.parent.mkdir(exist_ok=True)

class EmailHeaderAnalyzerTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Forest Email Header Analyzer Trainer - Blue Team")
        self.root.geometry("960x720")
        self.root.configure(bg="#1e1e1e")

        self.bg_color = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.yes_fg = "#22c55e"
        self.no_fg = "#ef4444"
        self.button_bg = "#1a1a1a"

        self.scenarios = [
            {"header": "From: support@bankofamerica-security.com\nReceived: from suspicious-ip.example.com", "risk": "High", "reason": "Spoofed sender + suspicious received-from", "feedback_correct": "✅ Correct! Spoofed From + bad Received = phishing.", "feedback_incorrect": "❌ Incorrect. This is a classic spoof."},
            {"header": "From: noreply@amazon.com\nReceived: from amazon-smtp.amazon.com", "risk": "Low", "reason": "Legitimate Amazon headers", "feedback_correct": "✅ Correct! Valid Amazon headers.", "feedback_incorrect": "❌ Incorrect. This is legitimate."},
        ]

        self.current = 0
        self.score = 0
        self.log = []
        self.start_time = datetime.datetime.now()

        self.create_ui()
        self.load_scenario()

    def create_ui(self):
        header = tk.Label(self.root, text="Forest Email Header Analyzer Trainer", font=("Helvetica", 20, "bold"), bg=self.bg_color, fg="#ffffff")
        header.pack(pady=15)

        self.progress_label = tk.Label(self.root, text="", font=("Helvetica", 12), bg=self.bg_color, fg="#aaaaaa")
        self.progress_label.pack(pady=5)

        self.card = tk.Frame(self.root, bg=self.card_bg, padx=30, pady=30)
        self.card.pack(pady=15, padx=40, fill="both", expand=True)

        self.header_label = tk.Label(self.card, text="", wraplength=820, justify="left", font=("Consolas", 12), bg=self.card_bg, fg="#e0e0e0")
        self.header_label.pack(fill="both", expand=True)

        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(pady=30)

        self.high_btn = tk.Button(btn_frame, text="HIGH RISK - Phishing", command=lambda: self.submit("High"),
                                  width=28, height=3, bg=self.button_bg, fg=self.no_fg, font=("Helvetica", 13, "bold"))
        self.high_btn.pack(side="left", padx=20)

        self.low_btn = tk.Button(btn_frame, text="LOW RISK - Legitimate", command=lambda: self.submit("Low"),
                                 width=28, height=3, bg=self.button_bg, fg=self.yes_fg, font=("Helvetica", 13, "bold"))
        self.low_btn.pack(side="left", padx=20)

        self.feedback_label = tk.Label(self.root, text="", wraplength=820, font=("Helvetica", 13), bg=self.bg_color)
        self.feedback_label.pack(pady=20)

    def load_scenario(self):
        if self.current >= len(self.scenarios):
            self.show_final_score()
            return
        s = self.scenarios[self.current]
        self.header_label.config(text=s["header"])
        self.feedback_label.config(text="")
        self.high_btn.config(state="normal")
        self.low_btn.config(state="normal")
        self.progress_label.config(text=f"Scenario {self.current + 1} of {len(self.scenarios)}")

    def submit(self, user_answer):
        s = self.scenarios[self.current]
        correct = user_answer == s["risk"]

        if correct:
            self.score += 1
            fb = s["feedback_correct"]
            color = "#22c55e"
        else:
            fb = s["feedback_incorrect"]
            color = "#ef4444"

        self.feedback_label.config(text=fb, fg=color)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {"timestamp": timestamp, "header": s["header"], "user_answer": user_answer, "correct": s["risk"]}
        self.log.append(entry)

        self.high_btn.config(state="disabled")
        self.low_btn.config(state="disabled")

        self.root.after(1800, self.next_scenario)

    def next_scenario(self):
        self.current += 1
        self.load_scenario()

    def show_final_score(self):
        total = len(self.scenarios)
        percentage = (self.score / total) * 100 if total > 0 else 0

        self.header_label.config(text=f"Training Complete!\nFinal Score: {self.score}/{total} ({percentage:.1f}%)")
        self.high_btn.config(state="disabled")
        self.low_btn.config(state="disabled")
        self.feedback_label.config(text="Great work. Header analysis is a powerful defense layer.", fg="#22c55e")

        session_data = {
            "session_date": datetime.datetime.now().isoformat(),
            "score": self.score,
            "total": total,
            "percentage": round(percentage, 1),
            "log": self.log
        }
        if VAULT_LOG.exists():
            with open(VAULT_LOG, "r") as f:
                history = json.load(f)
            history.append(session_data)
        else:
            history = [session_data]
        with open(VAULT_LOG, "w") as f:
            json.dump(history, f, indent=2)

        messagebox.showinfo("Session Complete", f"Email Header Training finished!\nScore: {self.score}/{total} ({percentage:.1f}%)")

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailHeaderAnalyzerTrainer(root)
    root.mainloop()
