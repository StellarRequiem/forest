import tkinter as tk
from tkinter import messagebox
import datetime
import json
import os
from pathlib import Path

VAULT_LOG = Path.home() / "ForestVault" / "phishing_sessions_v5.json"
VAULT_LOG.parent.mkdir(exist_ok=True)

class PhishingTrainerV5:
    def __init__(self, root):
        self.root = root
        self.root.title("Phishing Defense Trainer v5 - Blue Team Edition")
        self.root.geometry("960x760")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(True, True)

        self.bg_color = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.text_color = "#e0e0e0"
        self.yes_fg = "#22c55e"
        self.no_fg = "#ef4444"
        self.button_bg = "#1a1a1a"

        self.questions = [
            {"email": "Subject: You've been selected for a free iPhone 15 Pro!\n\nCongratulations! Click here: https://secure-login.com/claim", "correct": "Yes", "feedback_correct": "✅ Correct! Reward + urgency = classic phishing.", "feedback_incorrect": "❌ Incorrect. Never click unsolicited prize links."},
            {"email": "Subject: Urgent: Microsoft Account Suspension\n\nVerify now: https://login.microsoft.com/verify", "correct": "Yes", "feedback_correct": "✅ Correct! Microsoft never asks via email link.", "feedback_incorrect": "❌ Incorrect. Classic Microsoft impersonation."},
            {"email": "Subject: Amazon Order Shipped #A392184\n\nTrack here: https://www.amazon.com/gp/track", "correct": "No", "feedback_correct": "✅ Correct! Real Amazon shipping notice.", "feedback_incorrect": "❌ Incorrect. This is legitimate."},
            {"email": "Subject: Payroll Update Required\n\nVerify deposit: https://hr.company-internal.com/update", "correct": "Yes", "feedback_correct": "✅ Correct! HR never sends urgent links.", "feedback_incorrect": "❌ Incorrect. Phishing - contact HR directly."},
            {"email": "Subject: Bank Security Alert\n\nClick to secure account: https://bank-login.com", "correct": "Yes", "feedback_correct": "✅ Correct! Banks never ask you to click a link.", "feedback_incorrect": "❌ Incorrect. Classic bank phishing."},
        ]

        self.current = 0
        self.score = 0
        self.log = []
        self.start_time = datetime.datetime.now()

        self.create_ui()
        self.load_question()

    def create_ui(self):
        header = tk.Label(self.root, text="Phishing Defense Trainer v5", font=("Helvetica", 20, "bold"), bg=self.bg_color, fg="#ffffff")
        header.pack(pady=15)

        self.progress_label = tk.Label(self.root, text="", font=("Helvetica", 12), bg=self.bg_color, fg="#aaaaaa")
        self.progress_label.pack(pady=5)

        self.card = tk.Frame(self.root, bg=self.card_bg, padx=30, pady=30)
        self.card.pack(pady=15, padx=40, fill="both", expand=True)

        self.email_label = tk.Label(self.card, text="", wraplength=820, justify="left", font=("Helvetica", 13), bg=self.card_bg, fg=self.text_color)
        self.email_label.pack(fill="both", expand=True)

        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(pady=30)

        self.yes_btn = tk.Button(btn_frame, text="Yes - This is Phishing", command=lambda: self.submit("Yes"),
                                 width=34, height=3, bg=self.button_bg, fg=self.yes_fg, font=("Helvetica", 13, "bold"),
                                 activebackground="#111111", activeforeground=self.yes_fg)
        self.yes_btn.pack(side="left", padx=25)

        self.no_btn = tk.Button(btn_frame, text="No - This is Legitimate", command=lambda: self.submit("No"),
                                width=34, height=3, bg=self.button_bg, fg=self.no_fg, font=("Helvetica", 13, "bold"),
                                activebackground="#111111", activeforeground=self.no_fg)
        self.no_btn.pack(side="left", padx=25)

        self.feedback_label = tk.Label(self.root, text="", wraplength=820, font=("Helvetica", 13), bg=self.bg_color)
        self.feedback_label.pack(pady=20)

        self.score_label = tk.Label(self.root, text="Score: 0/0 (0%)", font=("Helvetica", 14, "bold"), bg=self.bg_color, fg="#ffffff")
        self.score_label.pack(pady=10)

        log_frame = tk.Frame(self.root, bg=self.bg_color)
        log_frame.pack(pady=10, padx=40, fill="both", expand=True)

        tk.Label(log_frame, text="Session Log", font=("Helvetica", 11), bg=self.bg_color, fg="#aaaaaa").pack(anchor="w")
        self.log_area = tk.Text(log_frame, height=9, bg="#2d2d2d", fg="#e0e0e0", font=("Consolas", 10), state="disabled")
        self.log_area.pack(fill="both", expand=True)

    def load_question(self):
        if self.current >= len(self.questions):
            self.show_final_score()
            return
        q = self.questions[self.current]
        self.email_label.config(text=q["email"])
        self.feedback_label.config(text="")
        self.yes_btn.config(state="normal")
        self.no_btn.config(state="normal")
        self.progress_label.config(text=f"Question {self.current + 1} of {len(self.questions)}")

    def submit(self, user_answer):
        q = self.questions[self.current]
        correct = user_answer == q["correct"]

        if correct:
            self.score += 1
            fb = q["feedback_correct"]
            color = "#22c55e"
        else:
            fb = q["feedback_incorrect"]
            color = "#ef4444"

        self.feedback_label.config(text=fb, fg=color)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {"timestamp": timestamp, "email": q["email"], "user_answer": user_answer, "correct_answer": q["correct"]}
        self.log.append(entry)

        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"[{timestamp}] → {user_answer} | Correct: {q['correct']}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

        self.yes_btn.config(state="disabled")
        self.no_btn.config(state="disabled")

        self.root.after(1800, self.next_question)

    def next_question(self):
        self.current += 1
        self.load_question()

    def show_final_score(self):
        total = len(self.questions)
        percentage = (self.score / total) * 100 if total > 0 else 0
        duration = (datetime.datetime.now() - self.start_time).seconds

        self.email_label.config(text=f"Training Session Complete!\n\nFinal Score: {self.score}/{total} ({percentage:.1f}%)\nTime: {duration//60}m {duration%60}s")
        self.yes_btn.config(state="disabled")
        self.no_btn.config(state="disabled")
        self.feedback_label.config(text="Excellent work. Keep sharpening your instincts.", fg="#22c55e")

        session_data = {
            "session_date": datetime.datetime.now().isoformat(),
            "score": self.score,
            "total": total,
            "percentage": round(percentage, 1),
            "duration_seconds": duration,
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

        messagebox.showinfo("Session Complete", f"Training finished!\nScore: {self.score}/{total} ({percentage:.1f}%)")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhishingTrainerV5(root)
    root.mainloop()
