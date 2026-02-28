from itertools import product

from engine.models import GameState, Piece, Board, GamePhase
from engine.game import (
    get_legal_placements,
    get_legal_piece_selections,
    make_move
)

def piece_to_code(p: Piece) -> str:
    coded_piece = ""
    if p.height:
        coded_piece = f"{coded_piece}T"
    else:
        coded_piece = f"{coded_piece}S"

    if p.color:
        coded_piece = f"{coded_piece}L"
    else:
        coded_piece = f"{coded_piece}D"

    if p.shape:
        coded_piece = f"{coded_piece}S"
    else:
        coded_piece = f"{coded_piece}R"

    if p.top:
        coded_piece = f"{coded_piece}H"
    else:
        coded_piece = f"{coded_piece}S"

    return coded_piece

def show_board(state: GameState) -> None:
    grid = state.board.grid

    print(" : 0    1    2    3   ")
    for i in range(4):
        row = f"{i}:"
        for j in range(4):
            cell = grid[i][j]
            if cell is None:
                row = f"{row} ____"
            else:
                row = f"{row} {piece_to_code(grid[i][j])}"
        print(row)

# Letter → bool for each position: 0=height, 1=color, 2=shape, 3=top (matches piece_to_code order)
_PIECE_LETTERS = (
    {"T": True, "S": False},  # Tall / Short
    {"L": True, "D": False},  # Light / Dark
    {"S": True, "R": False},  # Square / Round
    {"H": True, "S": False},  # Hollow / Solid
)

def _parse_piece_string(s: str) -> Piece | None:
    """Parse a 4-letter code to a Piece, or None if invalid."""
    if len(s) != 4:
        return None
    values = []
    for i, mapping in enumerate(_PIECE_LETTERS):
        if s[i] not in mapping:
            return None
        values.append(mapping[s[i]])
    return Piece(height=values[0], color=values[1], shape=values[2], top=values[3])

def parse_piece(legal_pieces: list[Piece]) -> Piece:
    while True:
        raw = input().strip().upper()
        piece = _parse_piece_string(raw)
        if piece is None:
            print("Please choose a valid piece.")
            continue
        if piece not in legal_pieces:
            print("That piece is not available.")
            continue
        return piece

def _parse_placement_string(s: str) -> tuple[int, int] | None:
    """Parse 'row,col' to (row, col) in 0-3, or None if invalid."""
    parts = [p.strip() for p in s.strip().split(",")]
    if len(parts) != 2:
        return None
    try:
        row, col = int(parts[0]), int(parts[1])
    except ValueError:
        return None
    if not (0 <= row <= 3 and 0 <= col <= 3):
        return None
    return (row, col)

def parse_placement(legal_placements: list[tuple[int, int]]) -> tuple[int, int]:
    while True:
        raw = input().strip()
        placement = _parse_placement_string(raw)
        if placement is None:
            print("Please choose a valid placement in the format: row, col (0-3, 0-3)")
            continue
        if placement in legal_placements:
            return placement
        print("That placement is not available.")

def show_turn(state: GameState) -> None:
    if state.current_phase == GamePhase.SELECT_PIECE:
        remaining = "Remaining: "
        for piece in state.remaining_pieces:
            remaining = f"{remaining}{piece_to_code(piece)} "
        print(remaining)
        print(f"\nPlayer {state.current_player}: choose a piece to give.")
    else:
        print(f"\nPlayer {state.current_player}: choose where to place [{piece_to_code(state.selected_piece)}].")


if __name__ == "__main__":
    remaining_pieces = [
        Piece(height=h, color=c, shape=s, top=t)
        for h, c, s, t in product([True, False], repeat=4)
    ]

    piece = Piece(height=True, color=True, shape=True, top=True)
    remaining_pieces.remove(piece)
    board = Board.empty()
    board.place(piece=piece, row=3, col=3)

    piece = Piece(height=False, color=False, shape=False, top=False)
    remaining_pieces.remove(piece)
    board.place(piece=piece, row=0, col=0)

    state = GameState(
        board=board,
        remaining_pieces=remaining_pieces,
        current_phase=GamePhase.PLACE_PIECE,
        selected_piece=remaining_pieces[0],
        current_player=0
    )

    show_board(state)
    show_turn(state)

    if state.current_phase == GamePhase.SELECT_PIECE:
        legal_pieces = get_legal_piece_selections(state)
        parse_piece(legal_pieces)
    else:
        legal_placements = get_legal_placements(state)
        parse_placement(legal_placements)
