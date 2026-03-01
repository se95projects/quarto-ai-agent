from itertools import product

import pytest
from src.engine.models import Piece, Board, GamePhase, GameState
from src.engine.game import (
    get_legal_placements,
    get_legal_piece_selections,
    make_move,
    check_winner
)
from src.interface.cli import piece_to_code, _parse_piece_string, _parse_placement_string

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

class TestCheckWinner:
    def test_check_winner_no_winner_empty_board(self):
        remaining_pieces = [
            Piece(height=h, color=c, shape=s, top=t)
            for h, c, s, t in product([True, False], repeat=4)
        ]
        current_player = 0
        state = GameState(
            board=Board.empty(),
            remaining_pieces=remaining_pieces,
            current_phase=GamePhase.SELECT_PIECE,
            selected_piece=None,
            current_player=current_player
        )

        result = check_winner(state)
        assert result is None

    def test_check_winner_no_winner(self):
        remaining_pieces = [
            Piece(height=h, color=c, shape=s, top=t)
            for h, c, s, t in product([True, False], repeat=4)
        ]
        current_player = 0
        pieces = [
            Piece(height=False, color=True, shape=True, top=True),
            Piece(height=True, color=False, shape=True, top=True),
            Piece(height=True, color=True, shape=False, top=True),
            Piece(height=True, color=True, shape=True, top=False)
        ]
        board = Board.empty()

        for i in range(4):
            remaining_pieces.remove(pieces[i])
            board.place(piece=pieces[i], row=i, col=i)

        state = GameState(
            board=board,
            remaining_pieces=remaining_pieces,
            current_phase=GamePhase.SELECT_PIECE,
            selected_piece=None,
            current_player=current_player
        )

        result = check_winner(state)
        assert result is None

    def test_check_winner_row(self):
        remaining_pieces = [
            Piece(height=h, color=c, shape=s, top=t)
            for h, c, s, t in product([True, False], repeat=4)
        ]
        current_player = 0
        pieces = [
            Piece(height=True, color=True, shape=True, top=True),
            Piece(height=True, color=False, shape=True, top=True),
            Piece(height=True, color=True, shape=False, top=True),
            Piece(height=True, color=True, shape=True, top=False)
        ]
        board = Board.empty()

        for i in range(4):
            remaining_pieces.remove(pieces[i])
            board.place(piece=pieces[i], row=0, col=i)

        state = GameState(
            board=board,
            remaining_pieces=remaining_pieces,
            current_phase=GamePhase.PLACE_PIECE,
            selected_piece=None,
            current_player=current_player
        )

        result = check_winner(state)
        assert result == 1-state.current_player

    def test_check_winner_column(self):
        remaining_pieces = [
            Piece(height=h, color=c, shape=s, top=t)
            for h, c, s, t in product([True, False], repeat=4)
        ]
        current_player = 0
        pieces = [
            Piece(height=True, color=True, shape=True, top=True),
            Piece(height=True, color=False, shape=True, top=True),
            Piece(height=True, color=True, shape=False, top=True),
            Piece(height=True, color=True, shape=True, top=False)
        ]
        board = Board.empty()

        for i in range(4):
            remaining_pieces.remove(pieces[i])
            board.place(piece=pieces[i], row=i, col=0)

        state = GameState(
            board=board,
            remaining_pieces=remaining_pieces,
            current_phase=GamePhase.PLACE_PIECE,
            selected_piece=None,
            current_player=current_player
        )

        result = check_winner(state)
        assert result == 1-state.current_player

    def test_check_winner_main_diag(self):
        remaining_pieces = [
            Piece(height=h, color=c, shape=s, top=t)
            for h, c, s, t in product([True, False], repeat=4)
        ]
        current_player = 0
        pieces = [
            Piece(height=True, color=True, shape=True, top=True),
            Piece(height=True, color=False, shape=True, top=True),
            Piece(height=True, color=True, shape=False, top=True),
            Piece(height=True, color=True, shape=True, top=False)
        ]
        board = Board.empty()

        for i in range(4):
            remaining_pieces.remove(pieces[i])
            board.place(piece=pieces[i], row=i, col=i)

        state = GameState(
            board=board,
            remaining_pieces=remaining_pieces,
            current_phase=GamePhase.PLACE_PIECE,
            selected_piece=None,
            current_player=current_player
        )

        result = check_winner(state)
        assert result == 1-state.current_player

    def test_check_winner_anti_diag(self):
        remaining_pieces = [
            Piece(height=h, color=c, shape=s, top=t)
            for h, c, s, t in product([True, False], repeat=4)
        ]
        current_player = 0
        pieces = [
            Piece(height=True, color=True, shape=True, top=True),
            Piece(height=True, color=False, shape=True, top=True),
            Piece(height=True, color=True, shape=False, top=True),
            Piece(height=True, color=True, shape=True, top=False)
        ]
        board = Board.empty()

        for i in range(4):
            remaining_pieces.remove(pieces[i])
            board.place(piece=pieces[i], row=i, col=3-i)

        state = GameState(
            board=board,
            remaining_pieces=remaining_pieces,
            current_phase=GamePhase.PLACE_PIECE,
            selected_piece=None,
            current_player=current_player
        )

        result = check_winner(state)
        assert result == 1-state.current_player

    def test_check_winner_square(self):
        remaining_pieces = [
            Piece(height=h, color=c, shape=s, top=t)
            for h, c, s, t in product([True, False], repeat=4)
        ]
        current_player = 0
        pieces = [
            Piece(height=True, color=True, shape=True, top=True),
            Piece(height=True, color=False, shape=True, top=True),
            Piece(height=True, color=True, shape=False, top=True),
            Piece(height=True, color=True, shape=True, top=False)
        ]
        board = Board.empty()

        p = 0
        for i in range(2):
            for j in range(2):
                remaining_pieces.remove(pieces[p])
                board.place(piece=pieces[p], row=i, col=j)
                p += 1

        state = GameState(
            board=board,
            remaining_pieces=remaining_pieces,
            current_phase=GamePhase.PLACE_PIECE,
            selected_piece=None,
            current_player=current_player
        )

        result = check_winner(state)
        assert result == 1-state.current_player


class TestCliParsing:
    """Unit tests for CLI helpers: piece_to_code, _parse_piece_string, _parse_placement_string."""

    def test_piece_to_code_all_true(self):
        p = Piece(height=True, color=True, shape=True, top=True)
        assert piece_to_code(p) == "TLSH"  # H = Hollow (top True)

    def test_piece_to_code_all_false(self):
        p = Piece(height=False, color=False, shape=False, top=False)
        assert piece_to_code(p) == "SDRS"

    def test_piece_to_code_mixed(self):
        p = Piece(height=True, color=False, shape=True, top=False)
        assert piece_to_code(p) == "TDSS"  # S = Solid (top False)

    def test_parse_piece_string_valid(self):
        assert _parse_piece_string("TLSH") == Piece(height=True, color=True, shape=True, top=True)
        assert _parse_piece_string("SDRS") == Piece(height=False, color=False, shape=False, top=False)
        assert _parse_piece_string("TLSS") == Piece(height=True, color=True, shape=True, top=False)
        assert _parse_piece_string("TDRH") == Piece(height=True, color=False, shape=False, top=True)

    def test_parse_piece_string_invalid_length(self):
        assert _parse_piece_string("") is None
        assert _parse_piece_string("TLS") is None
        assert _parse_piece_string("TLSSS") is None

    def test_parse_piece_string_invalid_letters(self):
        assert _parse_piece_string("TLSX") is None
        assert _parse_piece_string("XXYY") is None
        assert _parse_piece_string("T1SS") is None

    def test_parse_piece_string_roundtrip(self):
        p = Piece(height=True, color=False, shape=True, top=False)
        code = piece_to_code(p)
        assert _parse_piece_string(code) == p

    def test_parse_placement_string_valid(self):
        assert _parse_placement_string("0,0") == (0, 0)
        assert _parse_placement_string("1,2") == (1, 2)
        assert _parse_placement_string("3,3") == (3, 3)
        assert _parse_placement_string("1, 2") == (1, 2)
        assert _parse_placement_string("  2 , 1  ") == (2, 1)

    def test_parse_placement_string_invalid_format(self):
        assert _parse_placement_string("") is None
        assert _parse_placement_string("1") is None
        assert _parse_placement_string("1,2,3") is None
        assert _parse_placement_string("a,b") is None
        assert _parse_placement_string("1,b") is None
        assert _parse_placement_string("a,2") is None

    def test_parse_placement_string_out_of_range(self):
        assert _parse_placement_string("-1,0") is None
        assert _parse_placement_string("0,-1") is None
        assert _parse_placement_string("4,0") is None
        assert _parse_placement_string("0,4") is None
        assert _parse_placement_string("5,5") is None