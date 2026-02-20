from src.models import GameState, Piece

def get_legal_placements(state: GameState) -> list[tuple[int, int]]:
    return [
        (row, col) for row in range(4) for col in range(4) if state.board.grid[row][col] is None
    ]

def get_legal_piece_selections(state: GameState) -> list[Piece]:
    return state.remaining_pieces