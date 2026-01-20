import tkinter as tk
from tkinter import messagebox
import time
from typing import List, Tuple, Optional

HUMAN = "X"
AI = "O"
EMPTY = " "

# رنگ‌ها
BG = "#0f172a"          # سرمه‌ای تیره
PANEL = "#111827"       # پنل تیره
CARD = "#1f2937"        # کارت
BORDER = "#334155"      # مرز
TXT = "#e5e7eb"         # متن روشن

HUMAN_COLOR = "#22c55e"  # سبز
AI_COLOR = "#facc15"     # زرد
MUTED = "#94a3b8"        # خاکستری روشن

HIGHLIGHT_HUMAN = "#14532d"  # سبز تیره برای هایلایت
HIGHLIGHT_AI = "#713f12"     # زرد/قهوه‌ای تیره برای هایلایت

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
        self.root.title("Tic-Tac-Toe AI • Minimax vs Alpha-Beta")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.board = new_board()
        self.buttons = [[None]*3 for _ in range(3)]
        self.game_started = False

        self.algorithm = tk.StringVar(value="alphabeta")
        self.ai_starts = tk.BooleanVar(value=False)

        self.last_human: Optional[Tuple[int, int]] = None
        self.last_ai: Optional[Tuple[int, int]] = None

        # --------- Header ---------
        header = tk.Frame(self.root, bg=BG)
        header.grid(row=0, column=0, padx=14, pady=(14, 10), sticky="ew")

        title = tk.Label(header, text="Tic-Tac-Toe", fg=TXT, bg=BG, font=("Segoe UI", 18, "bold"))
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="Human (X) vs AI (O) — Compare Minimax and Alpha-Beta each AI turn",
            fg=MUTED, bg=BG, font=("Segoe UI", 10)
        )
        subtitle.pack(anchor="w")

        # --------- Main layout (left controls, right board) ---------
        main = tk.Frame(self.root, bg=BG)
        main.grid(row=1, column=0, padx=14, pady=(0, 14))

        left = tk.Frame(main, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        left.grid(row=0, column=0, padx=(0, 12), sticky="n")

        right = tk.Frame(main, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        right.grid(row=0, column=1, sticky="n")

        # --------- Controls panel ---------
        tk.Label(left, text="Settings", fg=TXT, bg=PANEL, font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=2, padx=12, pady=(12, 6), sticky="w"
        )

        tk.Label(left, text="AI algorithm", fg=MUTED, bg=PANEL, font=("Segoe UI", 9)).grid(
            row=1, column=0, padx=12, pady=(2, 2), sticky="w"
        )

        self.rb_minimax = tk.Radiobutton(
            left, text="Minimax", variable=self.algorithm, value="minimax",
            fg=TXT, bg=PANEL, selectcolor=CARD, activebackground=PANEL, activeforeground=TXT
        )
        self.rb_ab = tk.Radiobutton(
            left, text="Alpha-Beta", variable=self.algorithm, value="alphabeta",
            fg=TXT, bg=PANEL, selectcolor=CARD, activebackground=PANEL, activeforeground=TXT
        )
        self.rb_minimax.grid(row=2, column=0, padx=12, sticky="w")
        self.rb_ab.grid(row=2, column=1, padx=12, sticky="w")

        self.cb_ai_starts = tk.Checkbutton(
            left, text="AI starts first", variable=self.ai_starts,
            fg=TXT, bg=PANEL, selectcolor=CARD, activebackground=PANEL, activeforeground=TXT,
            command=self.maybe_start_ai
        )
        self.cb_ai_starts.grid(row=3, column=0, columnspan=2, padx=12, pady=(6, 10), sticky="w")

        self.status = tk.Label(left, text="Choose options then play (Human = X)", fg=TXT, bg=PANEL, font=("Segoe UI", 10))
        self.status.grid(row=4, column=0, columnspan=2, padx=12, pady=(0, 10), sticky="w")

        self.ai_move_label = tk.Label(left, text="AI move: -", fg=MUTED, bg=PANEL, font=("Segoe UI", 10))
        self.ai_move_label.grid(row=5, column=0, columnspan=2, padx=12, pady=(0, 6), sticky="w")

        self.compare_label = tk.Label(left, text="", fg=TXT, bg=PANEL, justify="left", font=("Consolas", 10))
        self.compare_label.grid(row=6, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="w")

        # Buttons row
        btnrow = tk.Frame(left, bg=PANEL)
        btnrow.grid(row=7, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="ew")

        self.reset_btn = tk.Button(
            btnrow, text="Reset / New Game", command=self.reset_game,
            bg=CARD, fg=TXT, activebackground=BORDER, activeforeground=TXT,
            relief="flat", padx=10, pady=6
        )
        self.reset_btn.pack(side="left")

        exit_btn = tk.Button(
            btnrow, text="Exit", command=self.root.destroy,
            bg="#7f1d1d", fg=TXT, activebackground="#991b1b", activeforeground=TXT,
            relief="flat", padx=10, pady=6
        )
        exit_btn.pack(side="right")

        # --------- Board panel ---------
        tk.Label(right, text="Board", fg=TXT, bg=PANEL, font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=3, padx=12, pady=(12, 6), sticky="w"
        )

        board_frame = tk.Frame(right, bg=PANEL)
        board_frame.grid(row=1, column=0, columnspan=3, padx=12, pady=(0, 12))

        for i in range(3):
            for j in range(3):
                btn = tk.Button(
                    board_frame,
                    text=" ",
                    width=4, height=2,
                    font=("Segoe UI", 22, "bold"),
                    bg=CARD, fg=TXT,
                    activebackground=BORDER, activeforeground=TXT,
                    relief="flat",
                    command=lambda i=i, j=j: self.human_move(i, j)
                )
                btn.grid(row=i, column=j, padx=6, pady=6)
                self.buttons[i][j] = btn

        # Legend
        legend = tk.Label(
            right,
            text="X = Human (green)   •   O = AI (yellow)",
            fg=MUTED, bg=PANEL, font=("Segoe UI", 9)
        )
        legend.grid(row=2, column=0, columnspan=3, padx=12, pady=(0, 12), sticky="w")

        self.enable_board_for_human()

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
        self.last_human = None
        self.last_ai = None

        self.status.config(text="Choose options then play (Human = X)")
        self.ai_move_label.config(text="AI move: -")
        self.compare_label.config(text="")

        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text=" ", fg=TXT, bg=CARD, state=tk.NORMAL)

        self.enable_board_for_human()

        # اگر AI-start فعال باشد، کاربر می‌تواند دوباره تیک بزند تا AI شروع کند
        if self.ai_starts.get():
            self.ai_starts.set(False)

    # ---------- helpers ----------
    def clear_highlights(self):
        # برگرداندن رنگ پس‌زمینه همه خانه‌ها
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(bg=CARD)

    def paint_cell(self, i, j, player):
        if player == HUMAN:
            self.buttons[i][j].config(fg=HUMAN_COLOR)
        elif player == AI:
            self.buttons[i][j].config(fg=AI_COLOR)

    def update_ui(self):
        for i in range(3):
            for j in range(3):
                val = self.board[i][j]
                if val == HUMAN:
                    self.buttons[i][j].config(text=val, fg=HUMAN_COLOR)
                elif val == AI:
                    self.buttons[i][j].config(text=val, fg=AI_COLOR)
                else:
                    self.buttons[i][j].config(text=" ", fg=TXT)

        # highlight last moves
        self.clear_highlights()
        if self.last_human is not None:
            i, j = self.last_human
            self.buttons[i][j].config(bg=HIGHLIGHT_HUMAN)
        if self.last_ai is not None:
            i, j = self.last_ai
            self.buttons[i][j].config(bg=HIGHLIGHT_AI)

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
            self.status.config(text="Game over. Press Reset / New Game.")
            return True
        return False

    # ---------- AI move + comparison ----------
    def ai_turn(self):
        # Compare BOTH algorithms on the same state
        mm_mv, mm_nodes, mm_t = best_move_minimax(self.board)
        ab_mv, ab_nodes, ab_t = best_move_alphabeta(self.board)

        chosen_name = "Minimax" if self.algorithm.get() == "minimax" else "Alpha-Beta"
        chosen_mv = mm_mv if self.algorithm.get() == "minimax" else ab_mv

        apply_move(self.board, chosen_mv, AI)
        self.last_ai = chosen_mv
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
            self.status.config(text="Your turn (X)")
            self.enable_board_for_human()

    # ---------- moves ----------
    def start_game_if_needed(self):
        if not self.game_started:
            self.game_started = True
            self.lock_options()

    def maybe_start_ai(self):
        if self.game_started:
            return
        if self.ai_starts.get():
            self.start_game_if_needed()
            self.status.config(text="AI thinking...")
            self.disable_board()
            self.root.after(120, self.ai_turn)
        else:
            self.status.config(text="Choose options then play (Human = X)")
            self.enable_board_for_human()

    def human_move(self, i, j):
        if not self.game_started and self.ai_starts.get():
            return
        if self.board[i][j] != EMPTY:
            return

        self.start_game_if_needed()

        apply_move(self.board, (i, j), HUMAN)
        self.last_human = (i, j)
        self.update_ui()

        if self.check_end():
            return

        self.status.config(text="AI thinking...")
        self.disable_board()
        self.root.after(120, self.ai_turn)


if __name__ == "__main__":
    TicTacToeGUI()
    tk.mainloop()
