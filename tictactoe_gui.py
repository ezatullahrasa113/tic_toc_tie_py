import tkinter as tk
from tkinter import messagebox
import time
from typing import List, Optional, Tuple

HUMAN = "X"
AI = "O"
EMPTY = " "

Board = List[List[str]]

# ================= GAME LOGIC =================

def new_board():
    return [[EMPTY]*3 for _ in range(3)]

def winner(b):
    lines = []
    lines.extend(b)  # rows
    lines.extend([[b[0][j], b[1][j], b[2][j]] for j in range(3)])  # cols
    lines.append([b[0][0], b[1][1], b[2][2]])
    lines.append([b[0][2], b[1][1], b[2][0]])
    for line in lines:
        if line[0] != EMPTY and line[0] == line[1] == line[2]:
            return line[0]
    return None

def is_full(b):
    return all(cell != EMPTY for row in b for cell in row)

def terminal_score(b, depth):
    w = winner(b)
    if w == AI:
        return 10 - depth
    if w == HUMAN:
        return -10 + depth
    if is_full(b):
        return 0
    return None

def available_moves(b):
    return [(i, j) for i in range(3) for j in range(3) if b[i][j] == EMPTY]

def apply_move(b, mv, p):
    b[mv[0]][mv[1]] = p

def undo_move(b, mv):
    b[mv[0]][mv[1]] = EMPTY

# ================= MINIMAX =================

def minimax(b, depth, is_max, counter):
    counter[0] += 1
    ts = terminal_score(b, depth)
    if ts is not None:
        return ts

    if is_max:
        best = -10_000
        for mv in available_moves(b):
            apply_move(b, mv, AI)
            val = minimax(b, depth+1, False, counter)
            undo_move(b, mv)
            best = max(best, val)
        return best
    else:
        best = 10_000
        for mv in available_moves(b):
            apply_move(b, mv, HUMAN)
            val = minimax(b, depth+1, True, counter)
            undo_move(b, mv)
            best = min(best, val)
        return best

def best_move_minimax(b):
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

def alphabeta(b, depth, is_max, alpha, beta, counter):
    counter[0] += 1
    ts = terminal_score(b, depth)
    if ts is not None:
        return ts

    if is_max:
        value = -10_000
        for mv in available_moves(b):
            apply_move(b, mv, AI)
            value = max(value, alphabeta(b, depth+1, False, alpha, beta, counter))
            undo_move(b, mv)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = 10_000
        for mv in available_moves(b):
            apply_move(b, mv, HUMAN)
            value = min(value, alphabeta(b, depth+1, True, alpha, beta, counter))
            undo_move(b, mv)
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value

def best_move_alphabeta(b):
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

        # choose algorithm BEFORE game
        self.algorithm = tk.StringVar(value="alphabeta")

        self.turn_label = tk.Label(self.root, text="Your turn (X)", font=("Arial", 12))
        self.turn_label.grid(row=0, column=0, columnspan=3, pady=(6, 2))

        algo_frame = tk.Frame(self.root)
        algo_frame.grid(row=1, column=0, columnspan=3)

        tk.Label(algo_frame, text="AI algorithm: ").pack(side=tk.LEFT)
        tk.Radiobutton(algo_frame, text="Minimax", variable=self.algorithm, value="minimax").pack(side=tk.LEFT)
        tk.Radiobutton(algo_frame, text="Alpha-Beta", variable=self.algorithm, value="alphabeta").pack(side=tk.LEFT)

        # Board buttons
        for i in range(3):
            for j in range(3):
                btn = tk.Button(
                    self.root, text=" ", width=6, height=3, font=("Arial", 20),
                    command=lambda i=i, j=j: self.human_move(i, j)
                )
                btn.grid(row=i+2, column=j, padx=2, pady=2)
                self.buttons[i][j] = btn

        # info panels
        self.ai_move_label = tk.Label(self.root, text="AI move: -", font=("Arial", 11))
        self.ai_move_label.grid(row=5, column=0, columnspan=3, pady=(6, 2))

        self.compare_label = tk.Label(self.root, text="", justify="left", font=("Consolas", 10))
        self.compare_label.grid(row=6, column=0, columnspan=3, pady=(2, 8))

        self.root.mainloop()

    def human_move(self, i, j):
        if self.board[i][j] != EMPTY:
            return

        apply_move(self.board, (i, j), HUMAN)
        self.update_ui()

        if self.check_end():
            return

        self.turn_label.config(text="AI thinking...")
        self.disable_board()

        # run AI after a tiny delay so UI updates
        self.root.after(80, self.ai_turn)

    def ai_turn(self):
        # IMPORTANT: compare BOTH algorithms on the same state
        mm_mv, mm_nodes, mm_t = best_move_minimax(self.board)
        ab_mv, ab_nodes, ab_t = best_move_alphabeta(self.board)

        # choose actual move based on selected algorithm
        if self.algorithm.get() == "minimax":
            chosen_mv = mm_mv
            chosen_name = "Minimax"
        else:
            chosen_mv = ab_mv
            chosen_name = "Alpha-Beta"

        # apply chosen move
        apply_move(self.board, chosen_mv, AI)
        self.update_ui()

        # show AI chosen move as 1..9
        k = chosen_mv[0] * 3 + chosen_mv[1] + 1
        self.ai_move_label.config(text=f"AI move ({chosen_name}): {k}")

        # show comparison side-by-side
        self.compare_label.config(
            text=(
                f"Minimax    | Nodes: {mm_nodes:<6} | Time: {mm_t*1000:>8.3f} ms\n"
                f"Alpha-Beta | Nodes: {ab_nodes:<6} | Time: {ab_t*1000:>8.3f} ms"
            )
        )

        if not self.check_end():
            self.turn_label.config(text="Your turn (X)")
            self.enable_board()

    def update_ui(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text=self.board[i][j])

    def disable_board(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(state=tk.DISABLED)

    def enable_board(self):
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == EMPTY:
                    self.buttons[i][j].config(state=tk.NORMAL)

    def check_end(self):
        w = winner(self.board)
        if w or is_full(self.board):
            if w == HUMAN:
                messagebox.showinfo("Result", "You win! (X)")
            elif w == AI:
                messagebox.showinfo("Result", "AI wins! (O)")
            else:
                messagebox.showinfo("Result", "Draw!")
            self.root.destroy()
            return True
        return False

# ================= RUN =================
if __name__ == "__main__":
    TicTacToeGUI()
