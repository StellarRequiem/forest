import tkinter as tk
import random
import time

class PhysicsScreensaver:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Forest Physics Screensaver")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#0a0a0a")
        self.root.overrideredirect(True)  # Remove window decorations

        self.canvas = tk.Canvas(self.root, bg="#0a0a0a", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Messages: mix of physics, security, and coding lingo
        self.messages = [
            "SHA256 verified", "Hash chain intact", "Drift detected", "Sandbox test passed",
            "F=ma", "E=mc²", "∇·E=ρ/ε₀", "Schrödinger eq", "Entropy increasing",
            "Prompt injection blocked", "Constitution enforced", "Vault sealed",
            "self.improve()", "for cycle in range(∞):", "while True: analyze()",
            "Quantum superposition", "Defensive vector mutated", "Tier 4 accuracy ↑",
            "No live exploits", "Ethical boundary respected", "Blue team hardened"
        ]

        self.drops = []
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Create initial drops
        for _ in range(48):
            x = random.randint(0, screen_width)
            y = random.randint(-400, -50)
            speed = random.uniform(1.8, 4.2)
            size = random.randint(10, 18)
            text = random.choice(self.messages)
            color = random.choice(["#22c55e", "#4ade80", "#86efac", "#eab308", "#60a5fa", "#c084fc"])
            
            self.drops.append({
                "x": x, "y": y, "speed": speed,
                "text": text, "color": color, "size": size,
                "item": None
            })

        self.root.bind("<Escape>", lambda e: self.root.quit())
        self.root.bind("<Button-1>", lambda e: self.root.quit())

        self.animate()

    def animate(self):
        for drop in self.drops:
            drop["y"] += drop["speed"]

            # Reset when off screen
            if drop["y"] > self.root.winfo_screenheight() + 100:
                drop["y"] = random.randint(-400, -50)
                drop["x"] = random.randint(0, self.root.winfo_screenwidth())
                drop["text"] = random.choice(self.messages)
                drop["color"] = random.choice(["#22c55e", "#4ade80", "#86efac", "#eab308", "#60a5fa", "#c084fc"])

            # Update or create text item
            if drop["item"]:
                self.canvas.delete(drop["item"])
            
            drop["item"] = self.canvas.create_text(
                drop["x"], drop["y"],
                text=drop["text"],
                font=("Courier", drop["size"], "normal"),
                fill=drop["color"],
                anchor="nw"
            )

        self.root.after(42, self.animate)  # ~24 fps

if __name__ == "__main__":
    print("Forest Physics Screensaver starting...")
    print("Press ESC or click anywhere to close")
    saver = PhysicsScreensaver()
    saver.root.mainloop()
