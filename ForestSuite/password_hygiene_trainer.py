import tkinter as tk
from tkinter import messagebox
import datetime
import json
import os
import math
import re
from pathlib import Path

VAULT_LOG = Path.home() / "ForestVault" / "password_sessions.json"
VAULT_LOG.parent.mkdir(exist_ok=True)

class PasswordTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Hygiene Trainer v1 - Blue Team Edition")
        self.root.geometry("860x620")
        self.root.configure(bg="#1e1e1e")

        self.bg_color = "#1e1e1e"
        self.card_bg = "#2d2d2d"
        self.text_color = "#e0e0e0"

        self.create_ui()

    def create_ui(self):
        tk.Label(self.root, text="Password Hygiene Trainer v1", font=("Helvetica", 18, "bold"), bg=self.bg_color, fg="#ffffff").pack(pady=15)

        tk.Label(self.root, text="Enter a password to test:", font=("Helvetica", 12), bg=self.bg_color, fg="#aaaaaa").pack(pady=5)

        self.entry = tk.Entry(self.root, width=50, font=("Consolas", 14), show="*", bg="#2d2d2d", fg="#e0e0e0")
        self.entry.pack(pady=10)

        self.test_btn = tk.Button(self.root, text="Test Password", command=self.test_password,
                                  bg="#3b82f6", fg="white", font=("Helvetica", 12, "bold"), width=20)
        self.test_btn.pack(pady=15)

        self.result_label = tk.Label(self.root, text="", wraplength=700, justify="left", font=("Helvetica", 12), bg=self.bg_color)
        self.result_label.pack(pady=10)

        self.log_area = tk.Text(self.root, height=12, bg="#2d2d2d", fg="#e0e0e0", font=("Consolas", 10), state="disabled")
        self.log_area.pack(pady=10, padx=40, fill="both", expand=True)

        tk.Label(self.root, text="Session Log", font=("Helvetica", 11), bg=self.bg_color, fg="#aaaaaa").pack(anchor="w", padx=40)

    def calculate_entropy(self, password):
        if not password:
            return 0
        charset_size = 0
        if re.search(r'[a-z]', password): charset_size += 26
        if re.search(r'[A-Z]', password): charset_size += 26
        if re.search(r'[0-9]', password): charset_size += 10
        if re.search(r'[^a-zA-Z0-9]', password): charset_size += 32
        return len(password) * math.log2(charset_size) if charset_size > 0 else 0

    def test_password(self):
        pw = self.entry.get().strip()
        if not pw:
            messagebox.showwarning("Empty", "Enter a password first.")
            return

        entropy = self.calculate_entropy(pw)
        score = "Very Weak"
        color = "#ef4444"
        feedback = []

        if entropy < 40:
            score = "Very Weak"
            feedback.append("❌ Extremely weak — easily cracked.")
        elif entropy < 60:
            score = "Weak"
            feedback.append("⚠️ Weak — improve length and variety.")
        elif entropy < 80:
            score = "Moderate"
            feedback.append("⚠️ Moderate — add special characters and length.")
        else:
            score = "Strong"
            color = "#22c55e"
            feedback.append("✅ Strong password!")

        # Common bad patterns
        if re.search(r'123|abc|password|admin|qwerty', pw.lower()):
            feedback.append("❌ Contains common patterns — avoid!")
        if len(set(pw)) < len(pw) * 0.7:
            feedback.append("❌ Too many repeated characters.")

        result_text = f"Password Strength: {score}\nEntropy: {entropy:.1f} bits\n\n" + "\n".join(feedback)
        self.result_label.config(text=result_text, fg=color)

        # Log to vault
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "password_length": len(pw),
            "entropy": round(entropy, 2),
            "strength": score,
            "feedback": feedback
        }

        if VAULT_LOG.exists():
            with open(VAULT_LOG, "r") as f:
                history = json.load(f)
            history.append(entry)
        else:
            history = [entry]

        with open(VAULT_LOG, "w") as f:
            json.dump(history, f, indent=2)

        # Update on-screen log
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"[{timestamp}] Strength: {score} | Entropy: {entropy:.1f} bits\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

        self.entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordTrainer(root)
    root.mainloop()
