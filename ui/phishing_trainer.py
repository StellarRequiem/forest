#!/usr/bin/env python3
"""
🌲 Forest Phishing Trainer v2.1-git — BlueAgent Powered
Interactive blue-team training with credentialing and logging.
"""
import sys
import os
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.blue_agent import BlueAgent

class PhishingTrainerAgent(BlueAgent):
    def __init__(self):
        super().__init__(name="PhishingTrainerAgent", model="llama3.2:3b", role="Phishing Defense Trainer")

    def run(self):
        if not self.credential:
            self.activate()

        print(f"🌲 Forest Phishing Trainer v2.1-git @ {datetime.now()}")
        self.log_action("PHISHING_TRAINER_LAUNCHED", "GUI started")

        # Simple Tkinter GUI (kept lightweight)
        root = tk.Tk()
        root.title("🌲 Forest Phishing Defense Trainer")
        root.geometry("900x700")
        root.configure(bg="#1e1e1e")

        ttk.Label(root, text="Phishing Defense Training", font=("Helvetica", 16, "bold"), background="#1e1e1e", foreground="#22c55e").pack(pady=10)

        # Score tracking
        self.score = 0
        self.total = 0
        score_label = ttk.Label(root, text=f"Score: {self.score}/{self.total}", font=("Helvetica", 12))
        score_label.pack(pady=5)

        # Sample questions (expandable)
        questions = [
            "You receive an email from 'support@bank.com' asking to click a link to verify your account. Is this safe?",
            "An email claims your PayPal account is suspended and asks for your password. Red flag?",
            "Email from a colleague with a suspicious attachment titled 'invoice.pdf.exe'. What do you do?",
        ]

        current_q = 0
        question_label = ttk.Label(root, text=questions[0], wraplength=800, font=("Helvetica", 11))
        question_label.pack(pady=20, padx=40)

        def answer(is_phishing):
            nonlocal current_q, self
            self.total += 1
            if is_phishing == (current_q in [0, 1, 2]):  # All are phishing in this sample
                self.score += 1
                messagebox.showinfo("Correct", "✅ Good catch! This is a phishing attempt.")
            else:
                messagebox.showwarning("Missed", "⚠️ This was a phishing attempt.")

            score_label.config(text=f"Score: {self.score}/{self.total}")

            current_q = (current_q + 1) % len(questions)
            question_label.config(text=questions[current_q])

            self.log_action("PHISHING_ANSWER", f"Q{current_q}: {'Phishing' if is_phishing else 'Legit'}")

        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="🚩 This is Phishing", command=lambda: answer(True)).pack(side="left", padx=20)
        ttk.Button(btn_frame, text="✅ This is Legitimate", command=lambda: answer(False)).pack(side="left", padx=20)

        ttk.Button(root, text="Quit Training", command=root.destroy).pack(pady=30)

        root.mainloop()

        self.log_action("PHISHING_TRAINER_CLOSED", f"Final score: {self.score}/{self.total}")

if __name__ == "__main__":
    agent = PhishingTrainerAgent()
    agent.run()
