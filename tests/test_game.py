from itertools import product

import pytest
from src.models import Piece, Board, GamePhase, GameState
from src.game import (
    get_legal_placements,
    get_legal_piece_selections,
    make_move
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

class TestMakeMove:
    def test_make_move_piece_not_given_during_select(self):
        state = GameState(
            board=Board.empty(),
            remaining_pieces=[],
            current_phase=GamePhase.SELECT_PIECE,
            selected_piece=None,
            current_player=0
        )

        with pytest.raises(ValueError, match="Must provide a piece to give during SELECT_PIECE phase."):
            make_move(state)

    def test_make_move_placement_not_given_during_place(self):
        state = GameState(
            board=Board.empty(),
            remaining_pieces=[],
            current_phase=GamePhase.PLACE_PIECE,
            selected_piece=None,
            current_player=0
        )

        with pytest.raises(ValueError, match="Must provide a placement during PLACE_PIECE phase."):
            make_move(state)

    def test_make_move_invalid_placement(self):
        piece = Piece(height=True, color=True, shape=True, top=True)
        placement = (0, 0)
        board = Board.empty()
        board.place(piece=piece, row=placement[0], col=placement[1])

        state = GameState(
            board=board,
            remaining_pieces=[],
            current_phase=GamePhase.PLACE_PIECE,
            selected_piece=None,
            current_player=0
        )

        with pytest.raises(ValueError, match="Position is already occupied or out of bounds."):
            make_move(state=state, placement=placement)

    def test_make_move_invalid_piece(self):
        remaining_pieces = [
            Piece(height=h, color=c, shape=s, top=t)
            for h, c, s, t in product([True, False], repeat=4)
        ]
        piece = Piece(height=True, color=True, shape=True, top=True)
        remaining_pieces.remove(piece)

        board = Board.empty()
        board.place(piece=piece, row=0, col=0)

        state = GameState(
            board=board,
            remaining_pieces=remaining_pieces,
            current_phase=GamePhase.SELECT_PIECE,
            selected_piece=piece,
            current_player=0
        )

        with pytest.raises(ValueError, match="Piece is not available for selection."):
            make_move(state=state, piece_to_give=piece)

    def test_make_move_valid_placement(self):
        remaining_pieces = [
            Piece(height=h, color=c, shape=s, top=t)
            for h, c, s, t in product([True, False], repeat=4)
        ]

        placement = (0,0)
        piece = Piece(height=True, color=True, shape=True, top=True)
        current_player = 0

        state = GameState(
            board=Board.empty(),
            remaining_pieces=remaining_pieces,
            current_phase=GamePhase.PLACE_PIECE,
            selected_piece=piece,
            current_player=current_player
        )

        result = make_move(state=state, placement=placement)
        assert result.board.grid[placement[0]][placement[1]] == piece
        assert result.current_phase == GamePhase.SELECT_PIECE
        assert result.selected_piece == None
        assert current_player == result.current_player

    def test_make_move_valid_piece(self):
        remaining_pieces = [
            Piece(height=h, color=c, shape=s, top=t)
            for h, c, s, t in product([True, False], repeat=4)
        ]
        piece = Piece(height=True, color=True, shape=True, top=True)
        current_player = 0

        state = GameState(
            board=Board.empty(),
            remaining_pieces=remaining_pieces,
            current_phase=GamePhase.SELECT_PIECE,
            selected_piece=None,
            current_player=current_player
        )

        result = make_move(state=state, piece_to_give=piece)
        assert result.selected_piece == piece
        assert piece not in result.remaining_pieces
        assert result.current_phase == GamePhase.PLACE_PIECE
        assert current_player != result.current_player