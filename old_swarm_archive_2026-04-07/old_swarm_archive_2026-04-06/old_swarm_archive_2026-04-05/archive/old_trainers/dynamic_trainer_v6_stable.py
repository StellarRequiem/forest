import tkinter as tk
from tkinter import messagebox
import datetime
import json
import os
import random
from pathlib import Path

VAULT_LOG = Path.home() / "ForestVault" / "dynamic_sessions.json"
QUESTION_BANK = Path.home() / "ForestVault" / "question_bank.json"
VAULT_LOG.parent.mkdir(exist_ok=True)
QUESTION_BANK.parent.mkdir(exist_ok=True)

class DynamicBlueTeamTrainer:
    def __init__(self, root=None):
        self.root = root
        self.is_headless = root is None

        self.bg_color = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.yes_fg = "#22c55e"
        self.no_fg = "#ef4444"
        self.button_bg = "#1a1a1a"

        self.current_tier = 1
        self.current = 0
        self.total_score = 0
        self.total_questions = 0
        self.log = []
        self.start_time = datetime.datetime.now()

        self.load_question_bank()

        if not self.is_headless:
            self.create_ui()
            self.load_question()
        else:
            print("Headless auto-run mode started.")

    def load_question_bank(self):
        if QUESTION_BANK.exists():
            with open(QUESTION_BANK) as f:
                self.bank = json.load(f)
        else:
            self.bank = [
                {"email": "Subject: Free iPhone 15 Pro - Claim Now!\n\nClick: https://secure-login.com/claim", "correct": "Yes", "feedback_correct": "✅ Correct! Reward + urgency = phishing.", "feedback_incorrect": "❌ Incorrect. Never click unsolicited prize links.", "tier": 1},
                {"email": "Subject: Microsoft Account Suspension\n\nVerify now: https://login.microsoft.com/verify", "correct": "Yes", "feedback_correct": "✅ Correct! Microsoft never asks via email link.", "feedback_incorrect": "❌ Incorrect. Classic impersonation.", "tier": 1},
                {"email": "Subject: Amazon Order Shipped\n\nTrack here: https://www.amazon.com/gp/track", "correct": "No", "feedback_correct": "✅ Correct! Real Amazon notice.", "feedback_incorrect": "❌ Incorrect. This is legitimate.", "tier": 1},
                {"email": "Subject: Payroll Update Required\n\nVerify deposit: https://hr.company-internal.com/update", "correct": "Yes", "feedback_correct": "✅ Correct! HR never sends urgent links.", "feedback_incorrect": "❌ Incorrect. Phishing - contact HR directly.", "tier": 2},
                {"email": "Subject: Bank Security Alert\n\nClick to secure account: https://bank-login.com", "correct": "Yes", "feedback_correct": "✅ Correct! Banks never ask you to click a link.", "feedback_incorrect": "❌ Incorrect. Classic bank phishing.", "tier": 2},
            ]
            with open(QUESTION_BANK, "w") as f:
                json.dump(self.bank, f, indent=2)

    def create_ui(self):
        header = tk.Label(self.root, text="Dynamic Blue Team Trainer v6.2", font=("Helvetica", 20, "bold"), bg=self.bg_color, fg="#ffffff")
        header.pack(pady=15)

        self.progress_label = tk.Label(self.root, text="", font=("Helvetica", 12), bg=self.bg_color, fg="#aaaaaa")
        self.progress_label.pack(pady=5)

        self.card = tk.Frame(self.root, bg=self.card_bg, padx=30, pady=30)
        self.card.pack(pady=15, padx=40, fill="both", expand=True)

        self.email_label = tk.Label(self.card, text="", wraplength=820, justify="left", font=("Helvetica", 13), bg=self.card_bg, fg="#e0e0e0")
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
        tier_questions = [q for q in self.bank if q.get("tier", 1) == self.current_tier]
        if not tier_questions:
            tier_questions = self.bank
        q = random.choice(tier_questions)
        self.current_question = q
        if not self.is_headless:
            self.email_label.config(text=q["email"])
            self.feedback_label.config(text="")
            self.yes_btn.config(state="normal")
            self.no_btn.config(state="normal")
            self.progress_label.config(text=f"Tier {self.current_tier} | Question {self.current + 1}")

    def submit(self, user_answer):
        q = self.current_question
        correct = user_answer == q["correct"]

        if correct:
            self.score += 1
            self.total_score += 1
            fb = q["feedback_correct"]
            color = "#22c55e"
        else:
            fb = q["feedback_incorrect"]
            color = "#ef4444"

        if not self.is_headless:
            self.feedback_label.config(text=fb, fg=color)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {"timestamp": timestamp, "email": q["email"], "user_answer": user_answer, "correct_answer": q["correct"], "tier": self.current_tier}
        self.log.append(entry)

        if not self.is_headless:
            self.log_area.config(state="normal")
            self.log_area.insert(tk.END, f"[{timestamp}] → {user_answer} | Correct: {q['correct']}\n")
            self.log_area.see(tk.END)
            self.log_area.config(state="disabled")

            self.yes_btn.config(state="disabled")
            self.no_btn.config(state="disabled")

            self.root.after(1800, self.next_question)
        else:
            self.next_question()

    def next_question(self):
        self.current += 1
        self.total_questions += 1
        if self.current >= 8:  # 8 questions per tier
            accuracy = (self.score / 8) * 100
            print(f"Tier {self.current_tier} complete. Accuracy: {accuracy:.1f}%")
            if accuracy >= 85:
                self.current_tier += 1
                print(f"Advancing to Tier {self.current_tier}")
            self.current = 0
            self.score = 0
        self.load_question()

    def show_final_score(self):
        percentage = (self.total_score / self.total_questions) * 100 if self.total_questions > 0 else 0

        if not self.is_headless:
            self.email_label.config(text=f"Session Complete!\nFinal Score: {self.total_score}/{self.total_questions} ({percentage:.1f}%)")
            self.yes_btn.config(state="disabled")
            self.no_btn.config(state="disabled")
            self.feedback_label.config(text="Excellent work. Keep sharpening your instincts.", fg="#22c55e")

        session_data = {
            "session_date": datetime.datetime.now().isoformat(),
            "score": self.total_score,
            "total": self.total_questions,
            "percentage": round(percentage, 1),
            "tier_reached": self.current_tier,
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

        if not self.is_headless:
            messagebox.showinfo("Session Complete", f"Training finished!\nScore: {self.total_score}/{self.total_questions} ({percentage:.1f}%)")
        else:
            print(f"Auto-run finished. Final Score: {self.total_score}/{self.total_questions} ({percentage:.1f}%) - Tier reached: {self.current_tier}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        trainer = DynamicBlueTeamTrainer(None)
        print("Starting headless auto-run with tier ramping...")
        for tier in range(1, 6):  # Try up to tier 5
            trainer.current_tier = tier
            trainer.current = 0
            trainer.score = 0
            print(f"\n--- Starting Tier {tier} ---")
            for q_num in range(8):
                trainer.load_question()
                # Smarter simulation: bias toward correct answer based on tier
                bias = min(0.95, 0.5 + (trainer.current_tier * 0.1))
                answer = trainer.current_question["correct"] if random.random() < bias else random.choice(["Yes", "No"])
                trainer.submit(answer)
            trainer.show_final_score()
        print("Auto-run finished.")
    else:
        root = tk.Tk()
        app = DynamicBlueTeamTrainer(root)
        root.mainloop()
