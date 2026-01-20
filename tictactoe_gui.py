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
    lines = b + list(zip(*b)) + [
        [b[0][0], b[1][1], b[2][2]],
        [b[0][2], b[1][1], b[2][0]]
    ]
    for line in lines:
        if line[0] != EMPTY and line.count(line[0]) == 3:
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
        best = -1e9
        for mv in available_moves(b):
            apply_move(b, mv, AI)
            best = max(best, minimax(b, depth+1, False, counter))
            undo_move(b, mv)
        return best
    else:
        best = 1e9
        for mv in available_moves(b):
            apply_move(b, mv, HUMAN)
            best = min(best, minimax(b, depth+1, True, counter))
            undo_move(b, mv)
        return best

def best_move_minimax(b):
    counter = [0]
    start = time.perf_counter()
    best_val = -1e9
    best_mv = None

    for mv in available_moves(b):
        apply_move(b, mv, AI)
        val = minimax(b, 1, False, counter)
        undo_move(b, mv)
        if val > best_val:
            best_val = val
            best_mv = mv

    return best_mv, counter[0], (time.perf_counter() - start)

# ================= ALPHA-BETA =================

def alphabeta(b, depth, is_max, alpha, beta, counter):
    counter[0] += 1
    ts = terminal_score(b, depth)
    if ts is not None:
        return ts

    if is_max:
        for mv in available_moves(b):
            apply_move(b, mv, AI)
            alpha = max(alpha, alphabeta(b, depth+1, False, alpha, beta, counter))
            undo_move(b, mv)
            if alpha >= beta:
                break
        return alpha
    else:
        for mv in available_moves(b):
            apply_move(b, mv, HUMAN)
            beta = min(beta, alphabeta(b, depth+1, True, alpha, beta, counter))
            undo_move(b, mv)
            if alpha >= beta:
                break
        return beta

def best_move_alphabeta(b):
    counter = [0]
    start = time.perf_counter()
    best_val = -1e9
    best_mv = None
    alpha, beta = -1e9, 1e9

    for mv in available_moves(b):
        apply_move(b, mv, AI)
        val = alphabeta(b, 1, False, alpha, beta, counter)
        undo_move(b, mv)
        if val > best_val:
            best_val = val
            best_mv = mv
        alpha = max(alpha, best_val)

    return best_mv, counter[0], (time.perf_counter() - start)

# ================= GUI =================

class TicTacToeGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tic-Tac-Toe AI")

        self.board = new_board()
        self.buttons = [[None]*3 for _ in range(3)]
        self.algorithm = tk.StringVar(value="alphabeta")

        self.info = tk.Label(self.root, text="Your turn (X)", font=("Arial", 12))
        self.info.grid(row=0, column=0, columnspan=3)

        tk.Radiobutton(self.root, text="Minimax", variable=self.algorithm,
                       value="minimax").grid(row=1, column=0)
        tk.Radiobutton(self.root, text="Alpha-Beta", variable=self.algorithm,
                       value="alphabeta").grid(row=1, column=2)

        for i in range(3):
            for j in range(3):
                btn = tk.Button(self.root, text=" ", width=6, height=3,
                                font=("Arial", 20),
                                command=lambda i=i, j=j: self.human_move(i, j))
                btn.grid(row=i+2, column=j)
                self.buttons[i][j] = btn

        self.stats = tk.Label(self.root, text="")
        self.stats.grid(row=5, column=0, columnspan=3)

        self.root.mainloop()

    def human_move(self, i, j):
        if self.board[i][j] != EMPTY:
            return
        self.board[i][j] = HUMAN
        self.update_ui()

        if self.check_end():
            return

        self.info.config(text="AI thinking...")
        self.root.after(100, self.ai_move)

    def ai_move(self):
        if self.algorithm.get() == "minimax":
            mv, nodes, t = best_move_minimax(self.board)
            name = "Minimax"
        else:
            mv, nodes, t = best_move_alphabeta(self.board)
            name = "Alpha-Beta"

        apply_move(self.board, mv, AI)
        self.update_ui()

        self.stats.config(
            text=f"{name} | Nodes: {nodes} | Time: {t*1000:.2f} ms"
        )

        if not self.check_end():
            self.info.config(text="Your turn (X)")

    def update_ui(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text=self.board[i][j])

    def check_end(self):
        w = winner(self.board)
        if w or is_full(self.board):
            if w == HUMAN:
                messagebox.showinfo("Result", "You win!")
            elif w == AI:
                messagebox.showinfo("Result", "AI wins!")
            else:
                messagebox.showinfo("Result", "Draw!")
            self.root.destroy()
            return True
        return False

# ================= RUN =================
if __name__ == "__main__":
    TicTacToeGUI()
