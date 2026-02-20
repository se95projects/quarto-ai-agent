from itertools import product

import pytest
from src.models import Piece, Board, GamePhase, GameState
from src.game import (
    get_legal_placements,
    get_legal_piece_selections
)

class TestGetLegalPlacement:
    def test_legal_placement_empty_board(self):
        state = GameState(
            board=Board.empty(),
            remaining_pieces=[],
            current_phase=GamePhase.SELECT_PIECE,
            selected_piece=None,
            current_player=0
        )
        result = get_legal_placements(state)
        assert len(result) == 16

    def test_legal_placement_full_board(self):
        piece = Piece(
            height=True,
            color=True,
            shape=True,
            top=True
        )
        board = Board(grid=[[piece] * 4 for _ in range(4)])
        state = GameState(
            board=board,
            remaining_pieces=[],
            current_phase=GamePhase.SELECT_PIECE,
            selected_piece=None,
            current_player=0
        )
        result = get_legal_placements(state)
        assert result == []

    def test_placement_excludes_occupied_square(self):
        piece = Piece(
            height=True,
            color=True,
            shape=True,
            top=True
        )
        board = Board.empty()
        board.place(piece, 0, 0)

        state = GameState(
            board=board,
            remaining_pieces=[],
            current_phase=GamePhase.SELECT_PIECE,
            selected_piece=None,
            current_player=0
        )
        result = get_legal_placements(state)
        assert (0,0) not in result

class TestLegalPieceSelection:
    def test_legal_piece_empty_board(self):
        remaining_pieces = [
            Piece(height=h, color=c, shape=s, top=t)
            for h, c, s, t in product([True, False], repeat=4)
        ]
        state = GameState(
            board=Board.empty(),
            remaining_pieces=remaining_pieces,
            current_phase=GamePhase.SELECT_PIECE,
            selected_piece=None,
            current_player=0
        )
        result = get_legal_piece_selections(state)
        assert len(result) == 16

    def test_legal_piece_full_board(self):
        piece = Piece(
            height=True,
            color=True,
            shape=True,
            top=True
        )
        board = Board(grid=[[piece] * 4 for _ in range(4)])

        state = GameState(
            board=board,
            remaining_pieces=[],
            current_phase=GamePhase.SELECT_PIECE,
            selected_piece=None,
            current_player=0
        )
        result = get_legal_piece_selections(state)
        assert result == []

    def test_legal_piece_placement_returns_remaining(self):
        remaining_pieces = [
            Piece(height=h, color=c, shape=s, top=t)
            for h, c, s, t in product([True, False], repeat=4)
        ]
        piece = Piece(height=True, color=True, shape=True, top=True)
        board = Board.empty()
        board.place(piece, 0, 0)
        remaining_pieces.remove(piece)

        state = GameState(
            board=board,
            remaining_pieces=remaining_pieces,
            current_phase=GamePhase.SELECT_PIECE,
            selected_piece=None,
            current_player=0
        )
        result = get_legal_piece_selections(state)
        assert piece not in result
        assert len(result) == 15