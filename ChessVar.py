# Author: Matthew Ilejay
# GitHub username: trilejay
# Date: 5/9/2024
# Description: Program that replicates the variant of chess called Atomic Chess, with a Piece class that represents a piece in the game, and a ChessVar class that represents the boards and rules of the game.

class Piece:
    """A class to represent a piece in the chess game, with a type, color, and position.
    Used by the ChessVar class."""

    def __init__(self, piece_type, color, position):
        """Constructor for the Piece class. Takes piece_type, color, and position as parameters.
        Initializes the required data members. All data members are private."""
        self._piece_type = piece_type
        self._color = color
        self._position = position

    def get_type(self):
        """Returns the type of piece."""
        return self._piece_type

    def get_color(self):
        """Returns the color of the piece."""
        return self._color

    def get_position(self):
        """Returns the current position of the piece."""
        return self._position

    def set_position(self, position):
        """Sets the position of the piece."""
        self._position = position


class ChessVar:
    """ChessVar class to represent the Atomic Chess game, played by two players.
    Uses the Piece class for piece management and board representation."""

    def __init__(self):
        """Constructor for ChessVar class. Takes no parameters.
        Initializes the board to the standard chess starting position.
        Initializes the turn to white's turn. All data members are private."""
        self._board = self._initialize_board()
        self._turn = 'white'
        self._game_state = 'UNFINISHED'

    def _initialize_board(self):
        """Initializes the board to the standard chess starting position."""
        board = {}
        white_pieces = {
            'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K', 'f1': 'B', 'g1': 'N', 'h1': 'R',
            'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P', 'f2': 'P', 'g2': 'P', 'h2': 'P'
        }
        for position, piece_type in white_pieces.items():
            board[position] = Piece(piece_type, 'white', position)

        black_pieces = {
            'a8': 'R', 'b8': 'N', 'c8': 'B', 'd8': 'Q', 'e8': 'K', 'f8': 'B', 'g8': 'N', 'h8': 'R',
            'a7': 'P', 'b7': 'P', 'c7': 'P', 'd7': 'P', 'e7': 'P', 'f7': 'P', 'g7': 'P', 'h7': 'P'
        }
        for position, piece_type in black_pieces.items():
            board[position] = Piece(piece_type, 'black', position)

        return board

    def get_game_state(self):
        """Returns the current state of the game."""
        return self._game_state

    def make_move(self, from_square, to_square):
        """Make a move from from_square to to_square.
        Removes pieces affected by explosions and updates the game state.
        Returns True if the move is successful, False otherwise."""
        if self._game_state != 'UNFINISHED':
            return False

        if from_square not in self._board:
            return False

        piece = self._board.get(from_square)
        if not piece or piece.get_color() != self._turn:
            return False

        if not self.is_valid_move(from_square, to_square):
            return False

        capturing_piece = self._board.get(to_square)
        piece.set_position(to_square)
        self._board[to_square] = piece
        del self._board[from_square]

        if capturing_piece:
            self.explode(to_square)
        if from_square in self._board:
            self.explode(from_square)

        if self.is_king_captured():
            if not self.is_king_captured(ignore_turn=True):
                self._game_state = 'BLACK_WON' if self._turn == 'black' else 'WHITE_WON'
            else:
                self._board[to_square] = capturing_piece
                piece.set_position(from_square)
                self._board[from_square] = piece
                del self._board[to_square]
                if from_square in self._board:
                    self.explode(from_square)
                if capturing_piece:
                    self.explode(to_square)
                self._game_state = 'UNFINISHED'  # Reset game state
                return False

        self.update_turn()
        return True

    def is_valid_move(self, from_square, to_square):
        """Checks if the move from from_square to to_square is valid."""
        if not self.is_on_board(to_square):
            return False

        piece = self._board.get(from_square)
        if not piece:
            return False

        if to_square in self._board and self._board[to_square].get_color() == piece.get_color():
            return False

        from_col, from_row = ord(from_square[0]), int(from_square[1])
        to_col, to_row = ord(to_square[0]), int(to_square[1])
        col_diff, row_diff = abs(to_col - from_col), abs(to_row - from_row)

        piece_type = piece.get_type()
        if piece_type == 'P':
            if piece.get_color() == 'white':
                if from_row == 2 and (row_diff == 2 and col_diff == 0) and to_square not in self._board:
                    return True
                if row_diff == 1 and col_diff == 0 and to_square not in self._board and to_row > from_row:
                    return True
                if row_diff == 1 and col_diff == 1 and to_square in self._board and self._board[
                    to_square].get_color() == 'black':
                    return True
            else:
                if from_row == 7 and (row_diff == 2 and col_diff == 0) and to_square not in self._board:
                    return True
                if row_diff == 1 and col_diff == 0 and to_square not in self._board and to_row < from_row:
                    return True
                if row_diff == 1 and col_diff == 1 and to_square in self._board and self._board[
                    to_square].get_color() == 'white':
                    return True
        elif piece_type == 'R':
            if col_diff == 0 or row_diff == 0:
                if self.is_path_clear(from_square, to_square):
                    return True
        elif piece_type == 'N':
            if col_diff == 2 and row_diff == 1 or col_diff == 1 and row_diff == 2:
                return True
        elif piece_type == 'B':
            if col_diff == row_diff:
                if self.is_path_clear(from_square, to_square):
                    return True
        elif piece_type == 'Q':
            if col_diff == row_diff or col_diff == 0 or row_diff == 0:
                if self.is_path_clear(from_square, to_square):
                    return True
        elif piece_type == 'K':
            if col_diff <= 1 and row_diff <= 1:
                return True

        return False

    def is_path_clear(self, from_square, to_square):
        """Checks if the path between from_square and to_square is clear of other pieces."""
        from_col, from_row = ord(from_square[0]), int(from_square[1])
        to_col, to_row = ord(to_square[0]), int(to_square[1])

        col_step = (to_col - from_col) // max(1, abs(to_col - from_col)) if to_col != from_col else 0
        row_step = (to_row - from_row) // max(1, abs(to_row - from_row)) if to_row != from_row else 0

        current_col, current_row = from_col + col_step, from_row + row_step

        while (current_col, current_row) != (to_col, to_row):
            current_square = f"{chr(current_col)}{current_row}"
            if current_square in self._board:
                return False
            current_col += col_step
            current_row += row_step

        return True

    def is_on_board(self, square):
        """Checks if a square is on the board."""
        return 'a' <= square[0] <= 'h' and 1 <= int(square[1]) <= 8

    def explode(self, square):
        """Handles the explosion when a piece is captured, removing affected pieces."""
        row, col = ord(square[0]), int(square[1])
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 'a' <= chr(r) <= 'h' and 1 <= c <= 8:
                pos = f"{chr(r)}{c}"
                if pos in self._board:
                    piece = self._board[pos]
                    if piece.get_type() == 'P' or piece.get_type() == 'p':
                        continue
                    del self._board[pos]

        if square in self._board:
            del self._board[square]

    def update_turn(self):
        """Updates the turn to the next player."""
        self._turn = 'black' if self._turn == 'white' else 'white'

    def is_king_captured(self, ignore_turn=False):
        """Checks if a king has been captured, which ends the game."""
        white_king_captured = False
        black_king_captured = False

        for piece in self._board.values():
            if piece.get_type() == 'K' and piece.get_color() == 'white':
                white_king_captured = True
            if piece.get_type() == 'K' and piece.get_color() == 'black':
                black_king_captured = True

        if ignore_turn:
            return white_king_captured and black_king_captured
        else:
            return not (white_king_captured and black_king_captured)

    def print_board(self):
        """Prints the current state of the board."""
        board_representation = [['.' for _ in range(8)] for _ in range(8)]
        for pos, piece in self._board.items():
            row, col = 8 - int(pos[1]), ord(pos[0]) - 97
            board_representation[row][col] = piece.get_type() if piece.get_color() == 'white' else piece.get_type().lower()

        for row in board_representation:
            print(' '.join(row))
