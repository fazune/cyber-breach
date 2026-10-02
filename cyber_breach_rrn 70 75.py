import tkinter as tk
from collections import deque, Counter
import random

# ==========================================
# NIGHTSHIFT - CYBER BREACH
# Runs using Python's built-in Tkinter
# ==========================================

CELL = 28
COLS = 21
ROWS = 17
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL

BG = "#090a10"
FLOOR = "#191b24"
WALL = "#343746"
PLAYER_COLOR = "#48d9ff"
GHOST_COLOR = "#ff405f"
KEY_COLOR = "#ffd84d"
EXIT_COLOR = "#5d9dff"

# A larger maze is generated for each new game. Odd-sized dimensions
# allow the maze-carving algorithm to build connected corridors.
def generate_maze():
    grid = [["#" for _ in range(COLS)] for _ in range(ROWS)]
    start = (1, 1)
    grid[1][1] = "."
    stack = [start]
    visited = {start}
    directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]

    while stack:
        x, y = stack[-1]
        choices = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < COLS - 1 and 1 <= ny < ROWS - 1 and (nx, ny) not in visited:
                choices.append((nx, ny, dx, dy))
        if not choices:
            stack.pop()
            continue
        nx, ny, dx, dy = random.choice(choices)
        grid[y + dy // 2][x + dx // 2] = "."
        grid[ny][nx] = "."
        visited.add((nx, ny))
        stack.append((nx, ny))

    # A few extra openings create loops and alternative routes.
    for y in range(1, ROWS - 1):
        for x in range(1, COLS - 1):
            if grid[y][x] == "#":
                if ((grid[y][x-1] == "." and grid[y][x+1] == ".") or
                    (grid[y-1][x] == "." and grid[y+1][x] == ".")):
                    if random.random() < 0.12:
                        grid[y][x] = "."
    return ["".join(row) for row in grid]

class HauntedHouse:
    def __init__(self, root):
        self.root = root
        self.root.title("NIGHTSHIFT: CYBER BREACH")
        self.root.resizable(True, True)
        self.root.configure(bg=BG)

        self.canvas = tk.Canvas(
            root, width=WIDTH, height=HEIGHT,
            bg=BG, highlightthickness=0
        )
        self.canvas.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.panel = tk.Frame(root, bg="#11121b", width=230)
        self.panel.grid(row=0, column=1, sticky="ns", padx=(0, 10), pady=10)
        self.panel.grid_propagate(False)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.title_label = tk.Label(
            self.panel, text="NIGHTSHIFT",
            font=("Arial", 16, "bold"),
            fg="#5d9dff", bg="#11121b"
        )
        self.title_label.pack(pady=(18, 8))

        tk.Label(
            self.panel, text="CYBER BREACH",
            font=("Arial", 10, "bold"),
            fg=GHOST_COLOR, bg="#11121b"
        ).pack(pady=5)

        self.score_label = tk.Label(
            self.panel, font=("Arial", 12, "bold"),
            fg="white", bg="#11121b"
        )
        self.score_label.pack(pady=12)

        tk.Label(
            self.panel, text="SECURITY MONITOR",
            font=("Arial", 11, "bold"),
            fg="#5d9dff", bg="#11121b"
        ).pack(pady=(10, 5))

        self.ai_label = tk.Label(
            self.panel, text="Initializing AI...",
            font=("Arial", 10), fg="#b6b7c8",
            bg="#11121b", wraplength=200,
            justify="left"
        )
        self.ai_label.pack(padx=12, pady=5)

        self.status_label = tk.Label(
            self.panel, text="",
            font=("Arial", 10, "bold"),
            fg=KEY_COLOR, bg="#11121b",
            wraplength=200
        )
        self.status_label.pack(pady=12)

        tk.Label(
            self.panel,
            text="CONTROLS\n\nArrow keys / WASD\nMove around\n\nCollect every access key\nFind the exit\nAvoid the Rogue AI",
            font=("Arial", 10),
            fg="white", bg="#11121b",
            justify="left"
        ).pack(pady=15)

        self.restart_button = tk.Button(
            self.panel, text="RESTART GAME",
            command=self.restart,
            font=("Arial", 11, "bold"),
            bg="#252b43", fg="white",
            activebackground="#3a4165",
            activeforeground="white",
            relief="flat", padx=12, pady=8
        )
        self.restart_button.pack(pady=10)

        self.home_button = tk.Button(
            self.panel, text="GO TO HOME", command=self.show_menu,
            font=("Arial", 11, "bold"),
            bg="#252b43", fg="white",
            activebackground="#3a4165",
            activeforeground="white",
            relief="flat", padx=12, pady=8
        )
        self.home_button.pack(pady=5)

        self.pause_button = tk.Button(
            self.panel, text="PAUSE (P)", command=self.toggle_pause,
            font=("Arial", 10, "bold"), bg="#252b43", fg="white",
            activebackground="#3a4165", activeforeground="white",
            relief="flat", padx=12, pady=7
        )
        self.pause_button.pack(pady=5)

        self.fullscreen_button = tk.Button(
            self.panel, text="FULL SCREEN (F11)", command=self.toggle_fullscreen,
            font=("Arial", 9, "bold"), bg="#252b43", fg="white",
            activebackground="#3a4165", activeforeground="white",
            relief="flat", padx=8, pady=7
        )
        self.fullscreen_button.pack(pady=5)

        self.root.bind("<KeyPress>", self.on_key)
        self.difficulty = None
        self.running = False
        self.paused = False
        self.fullscreen = False
        self.player_color = PLAYER_COLOR
        self.show_menu()

    def show_menu(self):
        self.running = False
        self.paused = False
        self.canvas.delete("all")
        # Reflow the start menu against the current canvas size so it also
        # uses the screen area when the window is maximized or fullscreen.
        canvas_w = max(WIDTH, self.canvas.winfo_width())
        canvas_h = max(HEIGHT, self.canvas.winfo_height())
        sx, sy = canvas_w / WIDTH, canvas_h / HEIGHT
        X = lambda value: int(value * sx)
        Y = lambda value: int(value * sy)
        self.canvas.create_rectangle(
            X(25), Y(25), X(WIDTH-25), Y(HEIGHT-25),
            fill="#11121b", outline="#5d9dff", width=3
        )
        self.canvas.create_text(
            X(WIDTH//2), Y(75), text="CYBER BREACH",
            fill="#5d9dff", font=("Arial", 22, "bold")
        )
        self.canvas.create_text(
            X(WIDTH//2), Y(130), text="Choose your Cyber Agent colour",
            fill="white", font=("Arial", 12, "bold")
        )
        palette = [
            ("CYAN", "#48d9ff"), ("LIME", "#9cff57"),
            ("BLUE", "#5d9dff"), ("RED", "#ff405f"),
            ("VIOLET", "#8b5cf6"), ("PURPLE", "#ad80ff"),
            ("PINK", "#ff83c8"), ("ORANGE", "#ffad5a"),
            ("WHITE", "#f0f2f8"), ("SILVER", "#b6b7c8")
        ]
        for i, (label, color) in enumerate(palette):
            button = tk.Button(
                self.canvas, text=label,
                command=lambda c=color: self.choose_player_color(c),
                font=("Arial", 8, "bold"), bg=color, fg="#090a10",
                activebackground=color, relief="flat", padx=5, pady=4
            )
            col, row = i % 5, i // 5
            self.canvas.create_window(
                X(WIDTH//2-120+col*60), Y(160+row*38), window=button
            )
        self.canvas.create_oval(
            X(WIDTH//2+180), Y(153), X(WIDTH//2+204), Y(177),
            fill=self.player_color, outline="white", width=2
        )
        self.canvas.create_text(
            X(WIDTH//2), Y(265), text="Select threat level",
            fill="white", font=("Arial", 14, "bold")
        )
        choices = [
            ("EASY", "Easy", "#527b69"),
            ("MEDIUM", "Medium", "#b77b45"),
            ("HARD", "Hard", "#a64e61")
        ]
        for i, (label, difficulty, color) in enumerate(choices):
            button = tk.Button(
                self.canvas, text=label,
                command=lambda d=difficulty: self.start_game(d),
                font=("Arial", 11, "bold"), bg=color, fg="white",
                activeforeground="white", relief="flat",
                padx=12, pady=8, cursor="hand2"
            )
            self.canvas.create_window(X(WIDTH//2-115+i*115), Y(315), window=button)
        self.canvas.create_text(
            X(WIDTH//2), Y(HEIGHT-75),
            text="WASD / Arrows: move  •  Collect access keys  •  Reach exit",
            fill="#b6b7c8", font=("Arial", 9)
        )

    def choose_player_color(self, color):
        self.player_color = color
        self.show_menu()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        self.fullscreen_button.config(
            text="EXIT FULL SCREEN (F11)" if self.fullscreen else "FULL SCREEN (F11)"
        )
        self.root.after(150, self.draw if self.running else self.show_menu)

    def on_canvas_resize(self, event=None):
        if getattr(self, "running", False):
            if not getattr(self, "paused", False):
                self.root.after_idle(self.draw)
        else:
            self.root.after_idle(self.show_menu)

    def toggle_pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        if self.paused:
            if hasattr(self, "timer"):
                try:
                    self.root.after_cancel(self.timer)
                except tk.TclError:
                    pass
            self.pause_button.config(text="RESUME (P)")
            self.message = "Game paused. Press P or Resume."
            self.draw()
            self.update_panel()
            self.canvas.create_rectangle(
                WIDTH//2-110, HEIGHT//2-45, WIDTH//2+110, HEIGHT//2+45,
                fill="#090a10", outline="#5d9dff", width=3
            )
            self.canvas.create_text(
                WIDTH//2, HEIGHT//2, text="PAUSED",
                fill="#5d9dff", font=("Arial", 22, "bold")
            )
        else:
            self.pause_button.config(text="PAUSE (P)")
            self.message = "Game resumed."
            self.draw()
            self.update_panel()
            self.timer = self.root.after(700, self.ghost_turn)

    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.restart()

    def restart(self):
        if self.difficulty is None:
            self.show_menu()
            return

        self.maze = generate_maze()
        self.player = (1, 1)
        self.ghost = (COLS - 2, 1)
        self.exit = (COLS - 2, ROWS - 2)

        key_counts = {"Easy": 4, "Medium": 7, "Hard": 10}
        self.total_keys = key_counts[self.difficulty]
        available = [(x, y) for y in range(1, ROWS-1)
                     for x in range(1, COLS-1)
                     if self.maze[y][x] == "." and (x, y) not in
                     {self.player, self.ghost, self.exit}]
        self.keys = set(random.sample(available, self.total_keys))
        self.collected = 0
        self.paused = False
        self.pause_button.config(text="PAUSE (P)")
        self.visits = Counter()
        self.visits[self.player] += 1

        self.last_move = (0, 0)
        self.turns = 0
        self.running = True
        self.ai_text = "AI initialized.\nSearching for player..."
        self.message = f"Collect {self.total_keys} access keys! ({self.difficulty})"

        if hasattr(self, "timer"):
            self.root.after_cancel(self.timer)

        self.draw()
        self.update_panel()
        first_delay = {"Easy": 850, "Medium": 700, "Hard": 500}[self.difficulty]
        self.timer = self.root.after(first_delay, self.ghost_turn)

    def is_floor(self, pos):
        x, y = pos
        return (
            0 <= x < COLS and 0 <= y < ROWS
            and self.maze[y][x] == "."
        )

    def neighbors(self, pos):
        x, y = pos
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nxt = (x + dx, y + dy)
            if self.is_floor(nxt):
                yield nxt

    # Breadth-first search: finds a walkable route
    def find_path(self, start, target):
        queue = deque([(start, [start])])
        seen = {start}

        while queue:
            current, path = queue.popleft()
            if current == target:
                return path

            for nxt in self.neighbors(current):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, path + [nxt]))

        return [start]

    def on_key(self, event):
        if event.keysym.lower() == "p":
            self.toggle_pause()
            return
        if event.keysym == "F11":
            self.toggle_fullscreen()
            return
        if not self.running or self.paused:
            return

        moves = {
            "Up": (0, -1), "w": (0, -1),
            "Down": (0, 1), "s": (0, 1),
            "Left": (-1, 0), "a": (-1, 0),
            "Right": (1, 0), "d": (1, 0)
        }

        if event.keysym not in moves:
            return

        dx, dy = moves[event.keysym]
        nxt = (self.player[0] + dx, self.player[1] + dy)

        if not self.is_floor(nxt):
            return

        self.player = nxt
        self.last_move = (dx, dy)
        self.visits[nxt] += 1

        if nxt in self.keys:
            self.keys.remove(nxt)
            self.collected += 1
            self.message = "You found a key!"
            self.ai_text = "Key detected.\nIncreasing hunt intensity."

        if self.player == self.ghost:
            self.lose()
            return

        if self.player == self.exit and self.collected == self.total_keys:
            self.win()
            return

        if self.player == self.exit and self.collected < self.total_keys:
            self.message = f"You need {self.total_keys - self.collected} more key(s)!"

        self.draw()
        self.update_panel()

    def ghost_turn(self):
        if not self.running:
            return

        self.turns += 1

        # AI analyses the player's movement history
        most_visited, count = self.visits.most_common(1)[0]
        repeated = count >= 4

        # Predict the next likely player position
        dx, dy = self.last_move
        predicted = (self.player[0] + dx, self.player[1] + dy)

        # Adapt its target if the predicted position is walkable
        if self.turns % 3 == 0 and self.is_floor(predicted):
            target = predicted
            self.ai_text = (
                "AI PREDICTION\n"
                "Tracking your movement.\n"
                "Predicting your next step."
            )
        else:
            target = self.player
            self.ai_text = (
                "AI HUNT MODE\n"
                "Calculating shortest path.\n"
                "Pursuing the agent."
            )

        if repeated:
            self.ai_text += (
                "\n\nPattern detected!\n"
                "You revisit the same area.\n"
                "AI is targeting that route."
            )

        # AI uses pathfinding to move toward its target
        path = self.find_path(self.ghost, target)
        if len(path) > 1:
            self.ghost = path[1]

        if self.ghost == self.player:
            self.lose()
            return

        # Ghost becomes faster as keys are collected
        self.draw()
        self.update_panel()

        base_speed = {"Easy": 600, "Medium": 520, "Hard": 360}[self.difficulty]
        speed = max(250, base_speed - self.collected * 35)
        self.timer = self.root.after(speed, self.ghost_turn)

    def lose(self):
        self.running = False
        self.message = "CYBER BREACH INTERCEPTED YOU!"
        self.ai_text = "AI HUNT SUCCESSFUL.\nPlayer intercepted."
        self.draw()
        self.update_panel()
        self.show_end("AGENT INTERCEPTED", "The Rogue AI caught you.")

    def win(self):
        self.running = False
        self.message = "YOU ESCAPED!"
        self.ai_text = "THREAT CONTAINED.\nAgent escaped the system."
        self.draw()
        self.update_panel()
        self.show_end("SYSTEM SECURED!", "You escaped the Rogue AI.")

    def show_end(self, title, subtitle):
        self.canvas.create_rectangle(
            90, 190, WIDTH-90, 340,
            fill="#090a10", outline="#5d9dff", width=3
        )
        self.canvas.create_text(
            WIDTH//2, 235, text=title,
            font=("Arial", 23, "bold"),
            fill="#5d9dff"
        )
        self.canvas.create_text(
            WIDTH//2, 285, text=subtitle,
            font=("Arial", 12),
            fill="white"
        )
        self.canvas.create_text(
            WIDTH//2, 315, text="Click RESTART GAME to play again",
            font=("Arial", 10),
            fill="#b6b7c8"
        )

    def draw(self):
        self.canvas.delete("all")

        for y in range(ROWS):
            for x in range(COLS):
                x1, y1 = x*CELL, y*CELL
                x2, y2 = x1+CELL, y1+CELL

                if self.maze[y][x] == "#":
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=WALL, outline="#282b3b"
                    )
                else:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=FLOOR, outline="#282b3b"
                    )

        # Exit
        ex, ey = self.exit
        self.canvas.create_rectangle(
            ex*CELL+7, ey*CELL+7,
            (ex+1)*CELL-7, (ey+1)*CELL-7,
            fill=EXIT_COLOR, outline="white", width=2
        )
        self.canvas.create_text(
            ex*CELL+CELL//2, ey*CELL+CELL//2,
            text="E", fill="#10251b",
            font=("Arial", 16, "bold")
        )

        # Keys
        for x, y in self.keys:
            cx, cy = x*CELL+CELL//2, y*CELL+CELL//2
            self.canvas.create_oval(
                cx-10, cy-10, cx+10, cy+10,
                fill=KEY_COLOR, outline="white", width=2
            )
            self.canvas.create_text(
                cx, cy, text="K",
                fill="#4b3510", font=("Arial", 10, "bold")
            )

        # Ghost
        gx, gy = self.ghost
        cx, cy = gx*CELL+CELL//2, gy*CELL+CELL//2
        self.canvas.create_polygon(
            cx, cy-18, cx+15, cy-9, cx+15, cy+9,
            cx, cy+18, cx-15, cy+9, cx-15, cy-9,
            fill=GHOST_COLOR, outline="#ff6b83", width=2
        )
        # Bright digital sensor marks
        self.canvas.create_rectangle(
            cx-9, cy-5, cx-3, cy+1, fill="#f4fbff", outline=""
        )
        self.canvas.create_rectangle(
            cx+3, cy-5, cx+9, cy+1, fill="#f4fbff", outline=""
        )
        self.canvas.create_line(
            cx-7, cy+8, cx+7, cy+8, fill="#390d24", width=2
        )

        # Player
        px, py = self.player
        cx, cy = px*CELL+CELL//2, py*CELL+CELL//2
        # Cyber operative: compact armour, helmet and illuminated visor.
        self.canvas.create_polygon(
            cx-12, cy-7, cx-9, cy-14, cx+9, cy-14,
            cx+12, cy-7, cx+15, cy+10, cx+8, cy+14,
            cx-8, cy+14, cx-15, cy+10,
            fill=self.player_color, outline="#e6eaff", width=2
        )
        self.canvas.create_rectangle(
            cx-10, cy-5, cx+10, cy+2,
            fill="#090a10", outline="#5d9dff", width=2
        )
        self.canvas.create_line(
            cx-5, cy-1, cx+5, cy-1, fill="#f4f6ff", width=2
        )
        self.canvas.create_line(
            cx-7, cy+8, cx+7, cy+8, fill="#090a10", width=2
        )

        # Resize the drawing to fill the available canvas area in fullscreen.
        canvas_w = max(1, self.canvas.winfo_width())
        canvas_h = max(1, self.canvas.winfo_height())
        scale_x = canvas_w / WIDTH
        scale_y = canvas_h / HEIGHT
        self.canvas.scale("all", 0, 0, scale_x, scale_y)

    def update_panel(self):
        self.score_label.config(
            text=f"🔑 KEYS: {self.collected}/{self.total_keys}\n"
                 f"🎚 LEVEL: {self.difficulty}\n\n"
                 f"📍 CYBER BREACH: {self.ghost}\n"
                 f"👣 MOVES: {self.turns}"
        )
        self.ai_label.config(text=self.ai_text)
        self.status_label.config(text=self.message)

root = tk.Tk()
game = HauntedHouse(root)
root.mainloop()
