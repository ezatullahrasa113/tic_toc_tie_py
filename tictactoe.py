from typing import List, Optional, Tuple

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
    # rows
    lines.extend([b[i] for i in range(3)])
    # cols
    lines.extend([[b[0][j], b[1][j], b[2][j]] for j in range(3)])
    # diagonals
    lines.append([b[0][0], b[1][1], b[2][2]])
    lines.append([b[0][2], b[1][1], b[2][0]])

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
    moves = []
    for i in range(3):
        for j in range(3):
            if b[i][j] == EMPTY:
                moves.append((i, j))
    return moves

def apply_move(b: Board, move: Tuple[int, int], player: str) -> None:
    i, j = move
    if b[i][j] != EMPTY:
        raise ValueError("Illegal move: cell is not empty")
    b[i][j] = player

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

def main_cli():
    b = new_board()
    current = HUMAN  # human starts
    print("Tic-Tac-Toe (X=Human, O=AI)\n")
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
            # فعلاً هوش مصنوعی نداریم: یک حرکت ساده انجام می‌دهد (بعداً minimax می‌گذاریم)
            mv = available_moves(b)[0]
            print(f"\nAI plays: {(mv[0]*3+mv[1]+1)}")
            apply_move(b, mv, AI)
            current = HUMAN

if __name__ == "__main__":
    main_cli()
