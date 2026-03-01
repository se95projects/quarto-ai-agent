from pydantic import BaseModel
from typing import Optional
from enum import Enum

class Piece(BaseModel, frozen=True):
    height: bool
    color: bool
    shape: bool
    top: bool

class Board(BaseModel):
    grid: list[list[Optional[Piece]]]

    def place(self, piece: Piece, row: int, col: int) -> None:
        self.grid[row][col] = piece

    def remove(self, row: int, col: int) -> None:
        self.grid[row][col] = None

    @staticmethod
    def empty() -> "Board":
        return Board(grid=[[None] * 4 for _ in range(4)])

class GamePhase(str, Enum):
    PLACE_PIECE = "place_piece"
    SELECT_PIECE = "select_piece"

class GameState(BaseModel):
    board: Board
    remaining_pieces: list[Piece]
    current_phase: GamePhase
    selected_piece: Optional[Piece]
    current_player: int