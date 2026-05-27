from src.board import Board
from src.ai import AI


def board_signature(board):
    signature = []

    for row in range(8):
        current_row = []

        for col in range(8):
            square = board.squares[row][col]

            if square.has_piece():
                piece = square.piece
                current_row.append((piece.color, piece.name, piece.moved))
            else:
                current_row.append(None)

        signature.append(tuple(current_row))

    return tuple(signature), board.last_move


def test_ai_evaluates_starting_board_as_equal():
    board = Board()
    ai = AI(color='black', depth=2)

    assert ai.evaluate(board) == 0


def test_ai_generates_legal_moves_for_black_starting_position():
    board = Board()
    ai = AI(color='black', depth=2)

    moves = ai.get_all_moves(board, 'black')

    assert len(moves) == 20
    assert all(piece.color == 'black' for piece, move in moves)


def test_ai_returns_a_legal_move_for_black():
    board = Board()
    ai = AI(color='black', depth=1)

    piece, move = ai.get_best_move(board)

    assert piece.color == 'black'
    assert board.squares[move.initial.row][move.initial.col].piece is piece


def test_ai_make_and_undo_temp_move_restores_board():
    board = Board()
    ai = AI(color='black', depth=1)
    piece, move = ai.get_random_move(board)
    before = board_signature(board)

    state = ai.make_temp_move(board, piece, move)
    assert board.squares[move.final.row][move.final.col].has_piece()

    ai.undo_temp_move(board, state)

    assert board_signature(board) == before


def test_get_best_move_does_not_mutate_board():
    board = Board()
    ai = AI(color='black', depth=2)
    before = board_signature(board)

    ai.get_best_move(board)

    assert board_signature(board) == before
