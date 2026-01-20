from typing import List, Optional, Tuple
import time

HUMAN = "X"
AI = "O"
EMPTY = " "

Board = List[List[str]]

def new_board() -> Board:
    return [[EMPTY for _ in range(3)] for _ in range(3)]

def print_board(b: Board) -> None:
    def cell(i, j):
        return b[i][j] if b[i][j] != EMPTY else str(i * 3 + j + 1)
    rows = []
    for i in range(3):
        rows.append(" | ".join(cell(i, j) for j in range(3)))
    print("\n---------\n".join(rows))

def winner(b: Board) -> Optional[str]:
    lines = []
    lines.extend([b[i] for i in range(3)])  # rows
    lines.extend([[b[0][j], b[1][j], b[2][j]] for j in range(3)])  # cols
    lines.append([b[0][0], b[1][1], b[2][2]])  # diag
    lines.append([b[0][2], b[1][1], b[2][0]])  # diag

    for line in lines:
        if line[0] != EMPTY and line[0] == line[1] == line[2]:
            return line[0]
    return None

def is_full(b: Board) -> bool:
    return all(b[i][j] != EMPTY for i in range(3) for j in range(3))

def game_over(b: Board) -> Tuple[bool, Optional[str]]:
    w = winner(b)
    if w:
        return True, w
    if is_full(b):
        return True, None
    return False, None

def available_moves(b: Board) -> List[Tuple[int, int]]:
    return [(i, j) for i in range(3) for j in range(3) if b[i][j] == EMPTY]

def apply_move(b: Board, move: Tuple[int, int], player: str) -> None:
    i, j = move
    if b[i][j] != EMPTY:
        raise ValueError("Illegal move: cell is not empty")
    b[i][j] = player

def undo_move(b: Board, move: Tuple[int, int]) -> None:
    i, j = move
    b[i][j] = EMPTY

def human_input_move(b: Board) -> Tuple[int, int]:
    while True:
        s = input("\nMove (1-9): ").strip()
        if not s.isdigit():
            print("Please enter a number 1..9")
            continue
        k = int(s)
        if not (1 <= k <= 9):
            print("Out of range. Enter 1..9")
            continue
        i = (k - 1) // 3
        j = (k - 1) % 3
        if b[i][j] != EMPTY:
            print("That cell is taken. Choose another.")
            continue
        return (i, j)

# ---------- SCORING ----------
def terminal_score(b: Board, depth: int) -> Optional[int]:
    """
    +10 - depth : AI wins sooner is better
    -10 + depth : AI loses later is better
    0 : draw
    """
    w = winner(b)
    if w == AI:
        return 10 - depth
    if w == HUMAN:
        return -10 + depth
    if is_full(b):
        return 0
    return None

# ---------- MINIMAX ----------
def minimax(b: Board, depth: int, is_maximizing: bool, counter: List[int]) -> int:
    counter[0] += 1

    ts = terminal_score(b, depth)
    if ts is not None:
        return ts

    if is_maximizing:
        best = -10_000
        for mv in available_moves(b):
            apply_move(b, mv, AI)
            val = minimax(b, depth + 1, False, counter)
            undo_move(b, mv)
            if val > best:
                best = val
        return best
    else:
        best = 10_000
        for mv in available_moves(b):
            apply_move(b, mv, HUMAN)
            val = minimax(b, depth + 1, True, counter)
            undo_move(b, mv)
            if val < best:
                best = val
        return best

def best_move_minimax(b: Board) -> Tuple[Tuple[int, int], int, float]:
    counter = [0]
    t0 = time.perf_counter()

    best_mv = None
    best_val = -10_000

    for mv in available_moves(b):
        apply_move(b, mv, AI)
        val = minimax(b, 1, False, counter)
        undo_move(b, mv)

        if val > best_val:
            best_val = val
            best_mv = mv

    t1 = time.perf_counter()
    assert best_mv is not None
    return best_mv, counter[0], (t1 - t0)

# ---------- ALPHA-BETA ----------
def alphabeta(b: Board, depth: int, is_maximizing: bool, alpha: int, beta: int, counter: List[int]) -> int:
    counter[0] += 1

    ts = terminal_score(b, depth)
    if ts is not None:
        return ts

    if is_maximizing:
        value = -10_000
        for mv in available_moves(b):
            apply_move(b, mv, AI)
            value = max(value, alphabeta(b, depth + 1, False, alpha, beta, counter))
            undo_move(b, mv)
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # prune
        return value
    else:
        value = 10_000
        for mv in available_moves(b):
            apply_move(b, mv, HUMAN)
            value = min(value, alphabeta(b, depth + 1, True, alpha, beta, counter))
            undo_move(b, mv)
            beta = min(beta, value)
            if alpha >= beta:
                break  # prune
        return value

def best_move_alphabeta(b: Board) -> Tuple[Tuple[int, int], int, float]:
    counter = [0]
    t0 = time.perf_counter()

    best_mv = None
    best_val = -10_000
    alpha = -10_000
    beta = 10_000

    for mv in available_moves(b):
        apply_move(b, mv, AI)
        val = alphabeta(b, 1, False, alpha, beta, counter)
        undo_move(b, mv)

        if val > best_val:
            best_val = val
            best_mv = mv

        alpha = max(alpha, best_val)  # tighten root alpha

    t1 = time.perf_counter()
    assert best_mv is not None
    return best_mv, counter[0], (t1 - t0)

# ---------- UTILS ----------
def algo_choice() -> str:
    while True:
        s = input("Choose AI algorithm: [1] Minimax  [2] Alpha-Beta : ").strip()
        if s == "1":
            return "minimax"
        if s == "2":
            return "alphabeta"
        print("Please enter 1 or 2.")

def ai_play(b: Board, algo: str) -> None:
    # For project comparison: we can also compute BOTH metrics every AI turn (optional)
    if algo == "minimax":
        mv, nodes, sec = best_move_minimax(b)
        name = "Minimax"
    else:
        mv, nodes, sec = best_move_alphabeta(b)
        name = "Alpha-Beta"

    print(f"\nAI ({name}) plays: {mv[0]*3+mv[1]+1}")
    print(f"Nodes evaluated: {nodes}")
    print(f"Time: {sec*1000:.3f} ms")
    apply_move(b, mv, AI)

def main_cli():
    b = new_board()
    current = HUMAN  # human starts
    algo = algo_choice()

    print("\nTic-Tac-Toe (X=Human, O=AI)")
    print(f"AI algorithm: {algo}\n")

    while True:
        print_board(b)
        over, w = game_over(b)
        if over:
            if w == HUMAN:
                print("\nHuman wins!")
            elif w == AI:
                print("\nAI wins!")
            else:
                print("\nDraw!")
            break

        if current == HUMAN:
            mv = human_input_move(b)
            apply_move(b, mv, HUMAN)
            current = AI
        else:
            ai_play(b, algo)
            current = HUMAN

if __name__ == "__main__":
    main_cli()
