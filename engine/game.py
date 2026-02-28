from engine.models import GameState, Piece, GamePhase
from typing import Optional

def get_legal_placements(state: GameState) -> list[tuple[int, int]]:
    return [
        (row, col) for row in range(4) for col in range(4) if state.board.grid[row][col] is None
    ]

def get_legal_piece_selections(state: GameState) -> list[Piece]:
    return state.remaining_pieces

def make_move(
    state: GameState,
    placement: Optional[tuple[int, int]] = None,
    piece_to_give: Optional[Piece] = None
) -> GameState:

    if state.current_phase == GamePhase.SELECT_PIECE:
        if piece_to_give is None:
            raise ValueError("Must provide a piece to give during SELECT_PIECE phase.")

        legal_pieces = get_legal_piece_selections(state)

        if piece_to_give in legal_pieces:
            state.selected_piece = piece_to_give
            state.remaining_pieces.remove(piece_to_give)

            if state.current_player == 0:
                state.current_player = 1 
            else:
                state.current_player = 0

            state.current_phase = GamePhase.PLACE_PIECE
        else:
            raise ValueError("Piece is not available for selection.")

    elif state.current_phase == GamePhase.PLACE_PIECE:
        if placement is None:
            raise ValueError("Must provide a placement during PLACE_PIECE phase.")

        legal_placements = get_legal_placements(state)

        if placement in legal_placements:
            state.board.place(
                piece = state.selected_piece, 
                row = placement[0],
                col = placement[1]
            )
            state.selected_piece = None

            state.current_phase = GamePhase.SELECT_PIECE
        else:
            raise ValueError("Position is already occupied or out of bounds.")

    return state

def _pieces_share_attribute(pieces: list[Piece]):
    for attr in ("height", "color", "shape", "top"):
        if len(set(getattr(p, attr) for p in pieces)) == 1:
            return True
    return False

def check_winner(state: GameState):
    grid = state.board.grid

    # check rows
    for i in range(4):
        row = grid[i][0:]
        if None not in row and _pieces_share_attribute(row):
            return state.current_player

    # check columns
    for j in range(4):
        col = [grid[i][j] for i in range(4)]
        if None not in col and _pieces_share_attribute(col):
            return state.current_player

    # check diagonals
    top_left_diag = [grid[i][i] for i in range(4)]
    top_right_diag = [grid[i][3 - i] for i in range(4)]
    if None not in top_left_diag and _pieces_share_attribute(top_left_diag):
        return state.current_player
    if None not in top_right_diag and _pieces_share_attribute(top_right_diag):
        return state.current_player

    # check 2x2 squares
    for i in range(3):
        for j in range(3):
            square = [grid[r][c] for r in range(i, i + 2) for c in range(j, j + 2)]
            if None not in square and _pieces_share_attribute(square):
                return state.current_player

    return None