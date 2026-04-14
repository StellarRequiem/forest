import tkinter as tk
import random

class ClearScreensaver:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Forest Clear Screensaver")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#000000")
        self.root.overrideredirect(True)

        self.canvas = tk.Canvas(self.root, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.messages = [
            "SHA256 verified", "Hash chain intact", "No drift detected", "Sandbox test passed",
            "F=ma", "E=mc²", "∇·B=0", "Schrödinger", "Entropy rising",
            "Constitution enforced", "Ethical boundary held", "Vault sealed",
            "self.improve()", "while True: analyze()", "for cycle in range(∞)",
            "Prompt injection blocked", "Defensive vectors adapted", "Tier accuracy ↑",
            "Blue team hardened", "Red team simulated", "Forest online"
        ]

        self.drops = []
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        for _ in range(45):
            x = random.randint(0, screen_w)
            y = random.randint(-500, -50)
            speed = random.uniform(1.5, 3.8)
            size = random.randint(11, 17)
            text = random.choice(self.messages)
            color = random.choice(["#22c55e", "#4ade80", "#86efac", "#a3e635", "#67e8f9"])

            self.drops.append({
                "x": x,
                "y": y,
                "speed": speed,
                "text": text,
                "color": color,
                "size": size,
                "item": None
            })

        self.root.bind("<Escape>", lambda e: self.root.quit())
        self.root.bind("<Button-1>", lambda e: self.root.quit())

        self.animate()

    def animate(self):
        for drop in self.drops:
            drop["y"] += drop["speed"]

            if drop["y"] > self.root.winfo_screenheight() + 80:
                drop["y"] = random.randint(-600, -100)
                drop["x"] = random.randint(0, self.root.winfo_screenwidth())
                drop["text"] = random.choice(self.messages)
                drop["color"] = random.choice(["#22c55e", "#4ade80", "#86efac", "#a3e635", "#67e8f9"])

            if drop["item"]:
                self.canvas.delete(drop["item"])

            drop["item"] = self.canvas.create_text(
                drop["x"], drop["y"],
                text=drop["text"],
                font=("Courier", drop["size"], "normal"),
                fill=drop["color"],
                anchor="nw"
            )

        self.root.after(40, self.animate)   # smooth ~25 fps

if __name__ == "__main__":
    print("Forest Clear Screensaver starting...")
    print("ESC or click to close")
    saver = ClearScreensaver()
    saver.root.mainloop()
