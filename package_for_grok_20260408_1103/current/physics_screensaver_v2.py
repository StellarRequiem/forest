import tkinter as tk
import random

class PhysicsCoderScreenSaver:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.root.bind('<Escape>', lambda e: self.root.quit())

        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        # Physics + Coder/Programmer lingo mix
        self.lines = [
            # Physics
            "F = ma", "E = mc²", "∇·E = ρ/ε₀", "∇×B = μ₀J + μ₀ε₀∂E/∂t",
            "iħ ∂ψ/∂t = Ĥψ", "S = k ln W", "Δx Δp ≥ ħ/2", "E = hf",
            "v = u + at", "s = ut + ½at²", "F = G m₁m₂ / r²", "λ = h / p",
            "c = 1/√(μ₀ε₀)", "τ = r × F", "L = Iω", "KE = ½mv²",
            "Ψ(x,t) = A e^{i(kx - ωt)}", "E = γmc²", "a = GM/r²",

            # Coder / Programmer lingo
            "def __init__(self):", "return None", "import numpy as np",
            "git commit -m", "sudo rm -rf /", "while True:", "for i in range",
            "try: except:", "if __name__ == '__main__':", "self.root.mainloop()",
            "O(n log n)", "Big O", "O(1) access", "segmentation fault",
            "kernel panic", "Segmentation fault (core dumped)",
            "pip install --upgrade", "docker run -d", "kubectl apply -f",
            "async def", "await asyncio", "lambda x: x**2",
            "SELECT * FROM users", "rm -rf ~/.cache", "echo 'Hello World'",
            "buffer overflow", "SQL injection", "XSS vulnerability",
            "public static void main", "System.out.println", "null pointer",
            "race condition", "deadlock", "mutex lock", "git push --force",
            "404 Not Found", "HTTP 500", "Segmentation fault",
            "Neural net weights", "backpropagation", "gradient descent",
            "loss = mse(y_true, y_pred)", "torch.nn.Module",
            " ollama run qwen3:8b", "cuda out of memory"
        ]

        self.drops = []

        self.create_drops(48)   # nice dense rain

        self.root.after(35, self.update)

    def create_drops(self, count):
        for _ in range(count):
            text = random.choice(self.lines)
            x = random.randint(20, self.root.winfo_screenwidth() - 80)
            y = random.randint(-400, -30)
            speed = random.uniform(1.6, 5.8)
            size = random.randint(11, 19)

            # Random vibrant color
            r = random.randint(90, 255)
            g = random.randint(90, 255)
            b = random.randint(90, 255)
            color = f'#{r:02x}{g:02x}{b:02x}'

            text_id = self.canvas.create_text(
                x, y,
                text=text,
                fill=color,
                font=("Courier New", size, "bold"),
                anchor="nw"
            )

            self.drops.append({
                'id': text_id,
                'x': x,
                'y': y,
                'speed': speed,
                'text': text,
                'size': size,
                'color': color
            })

    def update(self):
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        for drop in self.drops[:]:
            drop['y'] += drop['speed']
            self.canvas.move(drop['id'], 0, drop['speed'])

            if drop['y'] > height + 120:
                self.canvas.delete(drop['id'])
                self.drops.remove(drop)

                # New drop
                text = random.choice(self.lines)
                x = random.randint(20, width - 100)
                y = random.randint(-350, -40)
                speed = random.uniform(1.6, 5.8)
                size = random.randint(11, 19)

                r = random.randint(90, 255)
                g = random.randint(90, 255)
                b = random.randint(90, 255)
                color = f'#{r:02x}{g:02x}{b:02x}'

                text_id = self.canvas.create_text(
                    x, y, text=text, fill=color,
                    font=("Courier New", size, "bold"), anchor="nw"
                )

                self.drops.append({
                    'id': text_id, 'x': x, 'y': y,
                    'speed': speed, 'text': text,
                    'size': size, 'color': color
                })

        self.root.after(33, self.update)

if __name__ == "__main__":
    root = tk.Tk()
    app = PhysicsCoderScreenSaver(root)
    root.mainloop()
