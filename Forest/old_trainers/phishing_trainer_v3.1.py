import tkinter as tk
from tkinter import messagebox
import datetime
import json
import os

class PhishingTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Phishing Defense Trainer v3.1 - Blue Team Edition")
        self.root.geometry("900x700")
        self.root.configure(bg="#1e1e1e")   # Dark background
        self.root.resizable(True, True)

        # Colors (professional dark theme)
        self.bg_color = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.text_color = "#e0e0e0"
        self.accent_yes = "#ff4d4d"      # Red for phishing
        self.accent_no = "#4ade80"       # Green for legitimate
        self.feedback_good = "#4ade80"
        self.feedback_bad = "#ff4d4d"

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
        header = tk.Label(self.root, text="Phishing Defense Trainer v3.1", font=("Helvetica", 20, "bold"), bg=self.bg_color, fg="#ffffff")
        header.pack(pady=15)

        # Progress
        self.progress_label = tk.Label(self.root, text="", font=("Helvetica", 12), bg=self.bg_color, fg="#aaaaaa")
        self.progress_label.pack(pady=5)

        # Email card
        self.card = tk.Frame(self.root, bg=self.card_bg, padx=20, pady=20, relief="flat")
        self.card.pack(pady=10, padx=30, fill="both", expand=True)

        self.email_label = tk.Label(self.card, text="", wraplength=780, justify="left", font=("Helvetica", 13), bg=self.card_bg, fg=self.text_color)
        self.email_label.pack(fill="both", expand=True)

        # Buttons frame
        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(pady=20)

        self.yes_btn = tk.Button(btn_frame, text="Yes - This is Phishing", command=lambda: self.submit("Yes"),
                                 width=28, height=2, bg=self.accent_yes, fg="white", font=("Helvetica", 12, "bold"),
                                 activebackground="#cc0000")
        self.yes_btn.pack(side="left", padx=15)

        self.no_btn = tk.Button(btn_frame, text="No - This is Legitimate", command=lambda: self.submit("No"),
                                width=28, height=2, bg=self.accent_no, fg="white", font=("Helvetica", 12, "bold"),
                                activebackground="#2e8b57")
        self.no_btn.pack(side="left", padx=15)

        # Feedback
        self.feedback_label = tk.Label(self.root, text="", wraplength=780, font=("Helvetica", 12), bg=self.bg_color, fg=self.feedback_good)
        self.feedback_label.pack(pady=15)

        # Score
        self.score_label = tk.Label(self.root, text="Score: 0/0 (0%)", font=("Helvetica", 14, "bold"), bg=self.bg_color, fg="#ffffff")
        self.score_label.pack(pady=8)

        # Log area
        log_frame = tk.Frame(self.root, bg=self.bg_color)
        log_frame.pack(pady=10, padx=30, fill="both", expand=True)

        tk.Label(log_frame, text="Session Log", font=("Helvetica", 11), bg=self.bg_color, fg="#aaaaaa").pack(anchor="w")
        self.log_area = tk.Text(log_frame, height=8, bg="#2d2d2d", fg="#e0e0e0", font=("Consolas", 10), state="disabled")
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

        progress = f"Question {self.current + 1} of {len(self.questions)}"
        self.progress_label.config(text=progress)

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

        # Update log display
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"[{timestamp}] → {user_answer} | Correct: {q['correct']}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

        # Disable buttons
        self.yes_btn.config(state="disabled")
        self.no_btn.config(state="disabled")

        # Next after short delay
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
        self.feedback_label.config(text="Excellent work. Review the log and keep sharpening your instincts.", fg=self.feedback_good)

        # Save log
        log_file = os.path.expanduser("~/PhishingDefenseTrainer_log.json")
        with open(log_file, "w") as f:
            json.dump(self.log, f, indent=2)

        messagebox.showinfo("Session Complete", 
            f"Training finished!\n\nScore: {self.score}/{total} ({percentage:.1f}%)\n\nDetailed log saved to:\n{log_file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhishingTrainer(root)
    root.mainloop()
