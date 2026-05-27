import math
import random

from src.const import ROWS, COLS
from src.piece import King, Pawn, Queen


class AI:
    """

    Features:
    - legal move generation using the existing Board.calc_moves method
    - board evaluation using material and small centre-control bonuses
    - random move selection
    - greedy move selection
    - minimax search
    - alpha-beta pruning

    The evaluation score is always from this AI's point of view:
    positive = good for the bot
    negative = good for the opponent
    """

    CENTER_SQUARES = {(3, 3), (3, 4), (4, 3), (4, 4)}
    CENTER_BONUS = 0.10

    def __init__(self, color='black', depth=2):
        self.color = color
        self.depth = depth

    def opponent_color(self, color=None):
        color = color or self.color
        return 'white' if color == 'black' else 'black'

    def get_all_moves(self, board, color):
        """
        Return every legal move for the given colour as (piece, move) pairs.
        The piece object returned belongs to the board passed into this method.
        """
        legal_moves = []

        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]

                if not square.has_piece():
                    continue

                piece = square.piece

                if piece.color != color:
                    continue

                piece.clear_moves()
                board.calc_moves(piece, row, col, bool=True)

                for move in piece.moves:
                    legal_moves.append((piece, move))

        return legal_moves

    def evaluate(self, board):
        """
        Score the board from the AI's perspective.
        Material is the primary factor; centre control is deliberately tiny.
        """
        score = 0

        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]

                if not square.has_piece():
                    continue

                piece = square.piece
                value = abs(piece.value)

                if (row, col) in self.CENTER_SQUARES:
                    value += self.CENTER_BONUS

                if piece.color == self.color:
                    score += value
                else:
                    score -= value

        return round(score, 4)

    def make_temp_move(self, board, piece, move):
        """
        Apply a move directly on the given board and return enough state to undo
        it exactly. This avoids expensive full-board copying during AI search.
        """
        initial = move.initial
        final = move.final
        initial_square = board.squares[initial.row][initial.col]
        final_square = board.squares[final.row][final.col]

        captured_square = final_square
        captured_piece = final_square.piece
        en_passant_capture = False
        promoted = False
        rook_state = None

        if isinstance(piece, Pawn):
            diagonal_move = final.col != initial.col
            empty_final = final_square.isempty()

            if diagonal_move and empty_final:
                en_passant_capture = True
                captured_square = board.squares[initial.row][final.col]
                captured_piece = captured_square.piece

        state = {
            'piece': piece,
            'move': move,
            'captured_square': captured_square,
            'captured_piece': captured_piece,
            'piece_moved': piece.moved,
            'last_move': board.last_move,
            'en_passant_capture': en_passant_capture,
            'promoted': promoted,
            'rook_state': rook_state,
        }

        initial_square.piece = None

        if en_passant_capture:
            captured_square.piece = None

        final_square.piece = piece

        if isinstance(piece, Pawn) and (final.row == 0 or final.row == 7):
            state['promoted'] = True
            final_square.piece = Queen(piece.color)

        if isinstance(piece, King) and abs(final.col - initial.col) == 2:
            state['rook_state'] = self._make_temp_castling_rook_move(board, move)

        piece.moved = True
        piece.clear_moves()
        board.last_move = move

        return state

    def undo_temp_move(self, board, state):
        """
        Restore the board to the exact state before make_temp_move().
        """
        piece = state['piece']
        move = state['move']
        initial = move.initial
        final = move.final
        initial_square = board.squares[initial.row][initial.col]
        final_square = board.squares[final.row][final.col]

        if state['rook_state']:
            self._undo_temp_castling_rook_move(board, state['rook_state'])

        final_square.piece = None
        initial_square.piece = piece

        if state['en_passant_capture']:
            state['captured_square'].piece = state['captured_piece']
        else:
            final_square.piece = state['captured_piece']

        piece.moved = state['piece_moved']
        board.last_move = state['last_move']
        piece.clear_moves()

    def simulate_move(self, board, move):
        """
        Kept only for compatibility with older tests/calls. It now mutates and
        restores the same board, then returns it. AI search no longer uses this.
        """
        piece = board.squares[move.initial.row][move.initial.col].piece

        if piece is None:
            return board

        state = self.make_temp_move(board, piece, move)
        self.undo_temp_move(board, state)

        return board

    def _make_temp_castling_rook_move(self, board, move):
        row = move.initial.row

        if move.final.col == 2:
            rook_initial_col = 0
            rook_final_col = 3
        else:
            rook_initial_col = 7
            rook_final_col = 5

        rook_initial_square = board.squares[row][rook_initial_col]
        rook_final_square = board.squares[row][rook_final_col]
        rook = rook_initial_square.piece

        rook_state = {
            'rook': rook,
            'rook_initial_square': rook_initial_square,
            'rook_final_square': rook_final_square,
            'rook_moved': rook.moved if rook else False,
            'rook_final_piece': rook_final_square.piece,
        }

        rook_initial_square.piece = None
        rook_final_square.piece = rook

        if rook:
            rook.moved = True

        return rook_state

    def _undo_temp_castling_rook_move(self, board, rook_state):
        rook = rook_state['rook']
        rook_state['rook_final_square'].piece = rook_state['rook_final_piece']
        rook_state['rook_initial_square'].piece = rook

        if rook:
            rook.moved = rook_state['rook_moved']

    def get_random_move(self, board):
        moves = self.get_all_moves(board, self.color)

        if not moves:
            return None, None

        return random.choice(moves)

    def get_greedy_move(self, board):
        """
        Choose the move that gives the best immediate evaluation.
        Useful as a simple bot level and as a fallback.
        """
        moves = self.get_all_moves(board, self.color)

        if not moves:
            return None, None

        best_score = -math.inf
        best_moves = []

        for piece, move in moves:
            state = self.make_temp_move(board, piece, move)
            score = self.evaluate(board)
            self.undo_temp_move(board, state)

            if score > best_score:
                best_score = score
                best_moves = [(piece, move)]
            elif score == best_score:
                best_moves.append((piece, move))

        return random.choice(best_moves)

    def get_best_move(self, board):
        """
        Choose the best move using alpha-beta minimax.
        Returns (piece, move). If there are no legal moves, returns (None, None).
        """
        moves = self.get_all_moves(board, self.color)

        if not moves:
            return None, None

        if self.depth <= 0:
            return self.get_random_move(board)

        best_score = -math.inf
        best_moves = []
        alpha = -math.inf
        beta = math.inf

        for piece, move in self._order_moves(board, moves):
            state = self.make_temp_move(board, piece, move)
            score = self.alpha_beta(
                board,
                self.depth - 1,
                alpha,
                beta,
                maximizing=False
            )
            self.undo_temp_move(board, state)

            if score > best_score:
                best_score = score
                best_moves = [(piece, move)]
            elif score == best_score:
                best_moves.append((piece, move))

            alpha = max(alpha, best_score)

        return random.choice(best_moves)

    def minimax(self, board, depth, maximizing):
        """
        Plain minimax implementation kept for DAA demonstration purposes.
        Prefer alpha_beta for actual play.
        """
        if depth == 0:
            return self.evaluate(board)

        color = self.color if maximizing else self.opponent_color()
        moves = self.get_all_moves(board, color)

        if not moves:
            return self.evaluate(board)

        if maximizing:
            best_score = -math.inf

            for piece, move in moves:
                state = self.make_temp_move(board, piece, move)
                score = self.minimax(board, depth - 1, maximizing=False)
                self.undo_temp_move(board, state)
                best_score = max(best_score, score)

            return best_score

        best_score = math.inf

        for piece, move in moves:
            state = self.make_temp_move(board, piece, move)
            score = self.minimax(board, depth - 1, maximizing=True)
            self.undo_temp_move(board, state)
            best_score = min(best_score, score)

        return best_score

    def alpha_beta(self, board, depth, alpha, beta, maximizing):
        """
        Minimax with alpha-beta pruning.
        Same result as minimax, usually fewer searched branches.
        """
        if depth == 0:
            return self.evaluate(board)

        color = self.color if maximizing else self.opponent_color()
        moves = self.get_all_moves(board, color)

        if not moves:
            return self.evaluate(board)

        ordered_moves = self._order_moves(board, moves)

        if maximizing:
            best_score = -math.inf

            for piece, move in ordered_moves:
                state = self.make_temp_move(board, piece, move)
                score = self.alpha_beta(
                    board,
                    depth - 1,
                    alpha,
                    beta,
                    maximizing=False
                )
                self.undo_temp_move(board, state)
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)

                if beta <= alpha:
                    break

            return best_score

        best_score = math.inf

        for piece, move in ordered_moves:
            state = self.make_temp_move(board, piece, move)
            score = self.alpha_beta(
                board,
                depth - 1,
                alpha,
                beta,
                maximizing=True
            )
            self.undo_temp_move(board, state)
            best_score = min(best_score, score)
            beta = min(beta, best_score)

            if beta <= alpha:
                break

        return best_score

    def _order_moves(self, board, moves):
        """
        Try captures first. This makes alpha-beta pruning more effective while
        keeping the implementation simple enough for a project explanation.
        """
        def move_priority(item):
            piece, move = item
            target_square = board.squares[move.final.row][move.final.col]

            if target_square.has_piece():
                return abs(target_square.piece.value)

            if (move.final.row, move.final.col) in self.CENTER_SQUARES:
                return self.CENTER_BONUS

            return 0

        return sorted(moves, key=move_priority, reverse=True)
