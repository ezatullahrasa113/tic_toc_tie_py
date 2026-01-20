import tkinter as tk
from tkinter import messagebox
import time
from typing import List, Tuple, Optional

HUMAN = "X"
AI = "O"
EMPTY = " "

HUMAN_COLOR = "green"
AI_COLOR = "gold"   # زرد
EMPTY_COLOR = "black"

Board = List[List[str]]

# ================= GAME LOGIC =================

def new_board() -> Board:
    return [[EMPTY]*3 for _ in range(3)]

def winner(b: Board) -> Optional[str]:
    lines = []
    lines.extend(b)  # rows
    lines.extend([[b[0][j], b[1][j], b[2][j]] for j in range(3)])  # cols
    lines.append([b[0][0], b[1][1], b[2][2]])
    lines.append([b[0][2], b[1][1], b[2][0]])
    for line in lines:
        if line[0] != EMPTY and line[0] == line[1] == line[2]:
            return line[0]
    return None

def is_full(b: Board) -> bool:
    return all(cell != EMPTY for row in b for cell in row)

def terminal_score(b: Board, depth: int) -> Optional[int]:
    w = winner(b)
    if w == AI:
        return 10 - depth
    if w == HUMAN:
        return -10 + depth
    if is_full(b):
        return 0
    return None

def available_moves(b: Board) -> List[Tuple[int, int]]:
    return [(i, j) for i in range(3) for j in range(3) if b[i][j] == EMPTY]

def apply_move(b: Board, mv: Tuple[int, int], p: str) -> None:
    b[mv[0]][mv[1]] = p

def undo_move(b: Board, mv: Tuple[int, int]) -> None:
    b[mv[0]][mv[1]] = EMPTY

# ================= MINIMAX =================

def minimax(b: Board, depth: int, is_max: bool, counter: List[int]) -> int:
    counter[0] += 1
    ts = terminal_score(b, depth)
    if ts is not None:
        return ts

    if is_max:
        best = -10_000
        for mv in available_moves(b):
            apply_move(b, mv, AI)
            val = minimax(b, depth + 1, False, counter)
            undo_move(b, mv)
            best = max(best, val)
        return best
    else:
        best = 10_000
        for mv in available_moves(b):
            apply_move(b, mv, HUMAN)
            val = minimax(b, depth + 1, True, counter)
            undo_move(b, mv)
            best = min(best, val)
        return best

def best_move_minimax(b: Board) -> Tuple[Tuple[int, int], int, float]:
    counter = [0]
    t0 = time.perf_counter()

    best_val = -10_000
    best_mv = None

    for mv in available_moves(b):
        apply_move(b, mv, AI)
        val = minimax(b, 1, False, counter)
        undo_move(b, mv)
        if val > best_val:
            best_val = val
            best_mv = mv

    t1 = time.perf_counter()
    return best_mv, counter[0], (t1 - t0)

# ================= ALPHA-BETA =================

def alphabeta(b: Board, depth: int, is_max: bool, alpha: int, beta: int, counter: List[int]) -> int:
    counter[0] += 1
    ts = terminal_score(b, depth)
    if ts is not None:
        return ts

    if is_max:
        value = -10_000
        for mv in available_moves(b):
            apply_move(b, mv, AI)
            value = max(value, alphabeta(b, depth + 1, False, alpha, beta, counter))
            undo_move(b, mv)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = 10_000
        for mv in available_moves(b):
            apply_move(b, mv, HUMAN)
            value = min(value, alphabeta(b, depth + 1, True, alpha, beta, counter))
            undo_move(b, mv)
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value

def best_move_alphabeta(b: Board) -> Tuple[Tuple[int, int], int, float]:
    counter = [0]
    t0 = time.perf_counter()

    best_val = -10_000
    best_mv = None
    alpha, beta = -10_000, 10_000

    for mv in available_moves(b):
        apply_move(b, mv, AI)
        val = alphabeta(b, 1, False, alpha, beta, counter)
        undo_move(b, mv)
        if val > best_val:
            best_val = val
            best_mv = mv
        alpha = max(alpha, best_val)

    t1 = time.perf_counter()
    return best_mv, counter[0], (t1 - t0)

# ================= GUI =================

class TicTacToeGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tic-Tac-Toe AI (Minimax vs Alpha-Beta)")

        self.board = new_board()
        self.buttons = [[None]*3 for _ in range(3)]

        self.game_started = False

        # pre-game options
        self.algorithm = tk.StringVar(value="alphabeta")
        self.ai_starts = tk.BooleanVar(value=False)  # False => Human starts

        self.turn_label = tk.Label(self.root, text="Choose options, then play. Human = X", font=("Arial", 12))
        self.turn_label.grid(row=0, column=0, columnspan=3, pady=(6, 2))

        opts = tk.Frame(self.root)
        opts.grid(row=1, column=0, columnspan=3)

        tk.Label(opts, text="AI algorithm: ").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.rb_minimax = tk.Radiobutton(opts, text="Minimax", variable=self.algorithm, value="minimax")
        self.rb_ab = tk.Radiobutton(opts, text="Alpha-Beta", variable=self.algorithm, value="alphabeta")
        self.rb_minimax.grid(row=0, column=1, sticky="w")
        self.rb_ab.grid(row=0, column=2, sticky="w")

        self.cb_ai_starts = tk.Checkbutton(opts, text="AI starts first", variable=self.ai_starts, command=self.maybe_start_ai)
        self.cb_ai_starts.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))

        # Board buttons
        for i in range(3):
            for j in range(3):
                btn = tk.Button(
                    self.root, text=" ", width=6, height=3,
                    font=("Arial", 20),
                    command=lambda i=i, j=j: self.human_move(i, j),
                    fg=EMPTY_COLOR
                )
                btn.grid(row=i+2, column=j, padx=2, pady=2)
                self.buttons[i][j] = btn

        self.ai_move_label = tk.Label(self.root, text="AI move: -", font=("Arial", 11))
        self.ai_move_label.grid(row=5, column=0, columnspan=3, pady=(6, 2))

        self.compare_label = tk.Label(self.root, text="", justify="left", font=("Consolas", 10))
        self.compare_label.grid(row=6, column=0, columnspan=3, pady=(2, 4))

        self.reset_btn = tk.Button(self.root, text="Reset / New Game", command=self.reset_game)
        self.reset_btn.grid(row=7, column=0, columnspan=3, pady=(6, 10))

        self.root.mainloop()

    # ---------- option lock/unlock ----------
    def lock_options(self):
        self.rb_minimax.config(state=tk.DISABLED)
        self.rb_ab.config(state=tk.DISABLED)
        self.cb_ai_starts.config(state=tk.DISABLED)

    def unlock_options(self):
        self.rb_minimax.config(state=tk.NORMAL)
        self.rb_ab.config(state=tk.NORMAL)
        self.cb_ai_starts.config(state=tk.NORMAL)

    # ---------- reset ----------
    def reset_game(self):
        self.board = new_board()
        self.game_started = False
        self.unlock_options()

        self.turn_label.config(text="Choose options, then play. Human = X")
        self.ai_move_label.config(text="AI move: -")
        self.compare_label.config(text="")

        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text=" ", fg=EMPTY_COLOR, state=tk.NORMAL)

    # ---------- helper ----------
    def update_ui(self):
        for i in range(3):
            for j in range(3):
                val = self.board[i][j]
                if val == HUMAN:
                    self.buttons[i][j].config(text=val, fg=HUMAN_COLOR)
                elif val == AI:
                    self.buttons[i][j].config(text=val, fg=AI_COLOR)
                else:
                    self.buttons[i][j].config(text=" ", fg=EMPTY_COLOR)

    def disable_board(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(state=tk.DISABLED)

    def enable_board_for_human(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(state=(tk.NORMAL if self.board[i][j] == EMPTY else tk.DISABLED))

    def check_end(self) -> bool:
        w = winner(self.board)
        if w or is_full(self.board):
            if w == HUMAN:
                messagebox.showinfo("Result", "You win! (X)")
            elif w == AI:
                messagebox.showinfo("Result", "AI wins! (O)")
            else:
                messagebox.showinfo("Result", "Draw!")
            self.disable_board()
            self.turn_label.config(text="Game over. Press Reset / New Game.")
            return True
        return False

    # ---------- AI move + comparison ----------
    def ai_turn(self):
        # Compare BOTH algorithms on the same state
        mm_mv, mm_nodes, mm_t = best_move_minimax(self.board)
        ab_mv, ab_nodes, ab_t = best_move_alphabeta(self.board)

        if self.algorithm.get() == "minimax":
            chosen_mv = mm_mv
            chosen_name = "Minimax"
        else:
            chosen_mv = ab_mv
            chosen_name = "Alpha-Beta"

        apply_move(self.board, chosen_mv, AI)
        self.update_ui()

        k = chosen_mv[0] * 3 + chosen_mv[1] + 1
        self.ai_move_label.config(text=f"AI move ({chosen_name}): {k}")

        self.compare_label.config(
            text=(
                f"Minimax    | Nodes: {mm_nodes:<6} | Time: {mm_t*1000:>8.3f} ms\n"
                f"Alpha-Beta | Nodes: {ab_nodes:<6} | Time: {ab_t*1000:>8.3f} ms"
            )
        )

        if not self.check_end():
            self.turn_label.config(text="Your turn (X)")
            self.enable_board_for_human()

    # ---------- moves ----------
    def start_game_if_needed(self):
        if not self.game_started:
            self.game_started = True
            self.lock_options()

    def maybe_start_ai(self):
        # اگر کاربر تیک "AI starts" را بزند، قبل از هر حرکت انسان، AI شروع کند
        if self.game_started:
            return  # بعد از شروع بازی دیگر تغییر نداریم
        if self.ai_starts.get():
            # شروع بازی با AI
            self.start_game_if_needed()
            self.turn_label.config(text="AI thinking...")
            self.disable_board()
            self.root.after(80, self.ai_turn)
        else:
            # برگشت به حالت human starts
            self.turn_label.config(text="Choose options, then play. Human = X")
            self.enable_board_for_human()

    def human_move(self, i, j):
        # اگر AI-start فعال باشد، اجازه نمی‌دهیم انسان قبل از حرکت AI بازی را شروع کند
        if not self.game_started and self.ai_starts.get():
            return

        if self.board[i][j] != EMPTY:
            return

        self.start_game_if_needed()

        apply_move(self.board, (i, j), HUMAN)
        self.update_ui()

        if self.check_end():
            return

        self.turn_label.config(text="AI thinking...")
        self.disable_board()
        self.root.after(80, self.ai_turn)

# ================= RUN =================
if __name__ == "__main__":
    TicTacToeGUI()
