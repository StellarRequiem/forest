import tkinter as tk
from tkinter import messagebox
import datetime
import json
import os

class PhishingTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Phishing Defense Trainer v3.3 - Blue Team Edition")
        self.root.geometry("940x740")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(True, True)

        # Colors
        self.bg_color = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.text_color = "#e0e0e0"

        # Strong contrast colors per your request
        self.yes_color = "#22c55e"      # Pleasant green for "Yes - This is Phishing"
        self.no_color = "#ef4444"       # Stop-sign red for "No - This is Legitimate"
        self.feedback_good = "#22c55e"
        self.feedback_bad = "#ef4444"

        self.questions = [
            {
                "email": "Subject: You've been selected for a free iPhone 15 Pro!\n\nCongratulations! Click here to claim your prize: https://secure-login.com/claim\n\nDon't miss out - offer ends soon!",
                "correct": "Yes",
                "feedback_correct": "✅ Correct! Classic reward phishing. Urgency + unrealistic prize = immediate red flag.",
                "feedback_incorrect": "❌ Incorrect. This is phishing. Legitimate companies do not give expensive prizes via random email links."
            },
            {
                "email": "Subject: Urgent Security Alert - Your Microsoft Account Will Be Suspended\n\nWe detected suspicious activity. Verify your identity immediately: https://login.microsoft.com/verify",
                "correct": "Yes",
                "feedback_correct": "✅ Correct! Microsoft will never ask you to click a link like this. Always go directly to the official site.",
                "feedback_incorrect": "❌ Incorrect. This is a very common phishing impersonation of Microsoft."
            },
            {
                "email": "Subject: Your Amazon Order Has Shipped - #A392184\n\nYour recent order has shipped. Track it here: https://www.amazon.com/gp/track\n\nThank you for shopping with Amazon.",
                "correct": "No",
                "feedback_correct": "✅ Correct! This looks legitimate. Amazon sends real shipping notifications with track links.",
                "feedback_incorrect": "❌ Incorrect. This appears to be a real Amazon notification."
            },
            {
                "email": "Subject: Payroll Update Required - Action Needed\n\nYour direct deposit information needs immediate verification. Click here: https://hr.company-internal.com/update",
                "correct": "Yes",
                "feedback_correct": "✅ Correct! HR will never send urgent payroll links via email. Always verify through official internal channels.",
                "feedback_incorrect": "❌ Incorrect. This is phishing. Contact HR directly instead of clicking any links."
            }
        ]

        self.current = 0
        self.score = 0
        self.log = []

        self.create_ui()
        self.load_question()

    def create_ui(self):
        # Header
        header = tk.Label(self.root, text="Phishing Defense Trainer v3.3", font=("Helvetica", 20, "bold"), bg=self.bg_color, fg="#ffffff")
        header.pack(pady=15)

        self.progress_label = tk.Label(self.root, text="", font=("Helvetica", 12), bg=self.bg_color, fg="#aaaaaa")
        self.progress_label.pack(pady=5)

        # Email card
        self.card = tk.Frame(self.root, bg=self.card_bg, padx=30, pady=30)
        self.card.pack(pady=15, padx=40, fill="both", expand=True)

        self.email_label = tk.Label(self.card, text="", wraplength=820, justify="left", font=("Helvetica", 13), bg=self.card_bg, fg=self.text_color)
        self.email_label.pack(fill="both", expand=True)

        # Buttons with forced contrast
        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(pady=30)

        self.yes_btn = tk.Button(btn_frame, text="Yes - This is Phishing", command=lambda: self.submit("Yes"),
                                 width=34, height=3, bg=self.yes_color, fg="#ffffff", font=("Helvetica", 13, "bold"),
                                 activebackground="#16a34a", activeforeground="#ffffff")
        self.yes_btn.pack(side="left", padx=25)

        self.no_btn = tk.Button(btn_frame, text="No - This is Legitimate", command=lambda: self.submit("No"),
                                width=34, height=3, bg=self.no_color, fg="#ffffff", font=("Helvetica", 13, "bold"),
                                activebackground="#b91c1c", activeforeground="#ffffff")
        self.no_btn.pack(side="left", padx=25)

        # Feedback
        self.feedback_label = tk.Label(self.root, text="", wraplength=820, font=("Helvetica", 13), bg=self.bg_color)
        self.feedback_label.pack(pady=20)

        # Score
        self.score_label = tk.Label(self.root, text="Score: 0/0 (0%)", font=("Helvetica", 14, "bold"), bg=self.bg_color, fg="#ffffff")
        self.score_label.pack(pady=10)

        # Log
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
            color = self.feedback_good
        else:
            fb = q["feedback_incorrect"]
            color = self.feedback_bad

        self.feedback_label.config(text=fb, fg=color)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "email": q["email"],
            "user_answer": user_answer,
            "correct_answer": q["correct"]
        }
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

        self.email_label.config(text=f"Training Session Complete!\n\nFinal Score: {self.score}/{total} ({percentage:.1f}%)")
        self.yes_btn.config(state="disabled")
        self.no_btn.config(state="disabled")
        self.feedback_label.config(text="Excellent work. Keep sharpening your instincts.", fg=self.feedback_good)

        log_file = os.path.expanduser("~/PhishingDefenseTrainer_log.json")
        with open(log_file, "w") as f:
            json.dump(self.log, f, indent=2)

        messagebox.showinfo("Session Complete", 
            f"Training finished!\n\nScore: {self.score}/{total} ({percentage:.1f}%)\n\nDetailed log saved to:\n{log_file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhishingTrainer(root)
    root.mainloop()
