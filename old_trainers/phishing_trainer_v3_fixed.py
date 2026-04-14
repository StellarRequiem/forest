import tkinter as tk
from tkinter import messagebox
import datetime
import json
import os

class PhishingTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Phishing Defense Trainer v3 - Blue Team Edition")
        self.root.geometry("850x650")
        self.root.configure(bg="#f8f9fa")

        self.questions = [
            {
                "email": "Subject: You've been selected for a free iPhone 15 Pro!\n\nCongratulations! Click here to claim your prize: https://secure-login.com/claim\n\nDon't miss out!",
                "correct": "Yes",
                "feedback_correct": "Correct! Classic reward-based phishing. Urgency + fake prize = red flag.",
                "feedback_incorrect": "Incorrect. This is phishing. Legitimate companies rarely give expensive prizes via unsolicited email links."
            },
            {
                "email": "Subject: Urgent: Your Microsoft Account Will Be Suspended\n\nWe detected suspicious activity. Verify immediately: https://login.microsoft.com/verify?user=you@email.com",
                "correct": "Yes",
                "feedback_correct": "Correct! Microsoft never asks you to click a link to verify your account this way.",
                "feedback_incorrect": "Incorrect. This is a common phishing tactic impersonating Microsoft."
            },
            {
                "email": "Subject: Your Amazon Order Has Shipped\n\nYour recent order #A3921 has shipped. Track it here: https://www.amazon.com/gp/track\n\nThank you,\nAmazon",
                "correct": "No",
                "feedback_correct": "Correct! This looks legitimate. Amazon does send real shipping notifications with track links.",
                "feedback_incorrect": "Incorrect. This appears to be a real Amazon notification. Always check the sender address carefully."
            },
            {
                "email": "Subject: Payroll Update Required\n\nYour direct deposit information needs verification. Click here: https://hr.company-internal.com/update",
                "correct": "Yes",
                "feedback_correct": "Correct! HR never sends urgent payroll links like this. Verify through official channels.",
                "feedback_incorrect": "Incorrect. This is phishing. Contact HR directly instead of clicking links."
            }
        ]

        self.current = 0
        self.score = 0
        self.log = []

        self.create_ui()
        self.load_question()

    def create_ui(self):
        tk.Label(self.root, text="Phishing Defense Trainer v3", font=("Arial", 18, "bold"), bg="#f8f9fa").pack(pady=10)

        self.email_label = tk.Label(self.root, text="", wraplength=780, justify="left", font=("Arial", 12), bg="#ffffff", bd=1, relief="solid", padx=10, pady=15)
        self.email_label.pack(pady=15, padx=20, fill="x")

        self.yes_btn = tk.Button(self.root, text="Yes - This is Phishing", command=lambda: self.submit("Yes"), width=30, height=2, bg="#dc3545", fg="white", font=("Arial", 11))
        self.yes_btn.pack(pady=8)

        self.no_btn = tk.Button(self.root, text="No - This is Legitimate", command=lambda: self.submit("No"), width=30, height=2, bg="#28a745", fg="white", font=("Arial", 11))
        self.no_btn.pack(pady=8)

        self.feedback_label = tk.Label(self.root, text="", wraplength=780, font=("Arial", 11), bg="#f8f9fa")
        self.feedback_label.pack(pady=15)

        self.score_label = tk.Label(self.root, text="Score: 0/0 (0%)", font=("Arial", 12, "bold"), bg="#f8f9fa")
        self.score_label.pack(pady=5)

        self.log_area = tk.Text(self.root, height=8, state="disabled", bg="#f8f9fa")
        self.log_area.pack(pady=10, padx=20, fill="x")

    def load_question(self):
        if self.current >= len(self.questions):
            self.show_final_score()
            return

        q = self.questions[self.current]
        self.email_label.config(text=q["email"])
        self.feedback_label.config(text="")
        self.yes_btn.config(state="normal")
        self.no_btn.config(state="normal")

    def submit(self, user_answer):
        q = self.questions[self.current]

        correct = user_answer == q["correct"]
        if correct:
            self.score += 1
            fb = q["feedback_correct"]
            color = "green"
        else:
            fb = q["feedback_incorrect"]
            color = "red"

        self.feedback_label.config(text=fb, fg=color)

        # Log
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "email": q["email"],
            "user_answer": user_answer,
            "correct_answer": q["correct"]
        }
        self.log.append(entry)

        # Update log display
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"[{timestamp}] {user_answer} | Correct: {q['correct']}\n")
        self.log_area.config(state="disabled")

        # Disable buttons
        self.yes_btn.config(state="disabled")
        self.no_btn.config(state="disabled")

        # Next question after delay
        self.root.after(2200, self.next_question)

    def next_question(self):
        self.current += 1
        self.load_question()

    def show_final_score(self):
        total = len(self.questions)
        percentage = (self.score / total) * 100 if total > 0 else 0

        self.email_label.config(text=f"Training Session Complete!\n\nFinal Score: {self.score}/{total} ({percentage:.1f}%)")
        self.yes_btn.config(state="disabled")
        self.no_btn.config(state="disabled")
        self.feedback_label.config(text="Great work! Review the log below for details.")

        # Save log
        log_file = os.path.expanduser("~/PhishingDefenseTrainer_log.json")
        with open(log_file, "w") as f:
            json.dump(self.log, f, indent=2)

        messagebox.showinfo("Session Complete", f"Training finished!\nScore: {self.score}/{total} ({percentage:.1f}%)\n\nLog saved to:\n{log_file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhishingTrainer(root)
    root.mainloop()
