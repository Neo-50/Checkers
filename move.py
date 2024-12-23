from cell import Cell
from piece import Piece

class Move:
    def __init__(self, piece: Piece, end: Cell, captures_piece: Piece = None):
        self.piece = piece
        self.end = end
        self.captures_piece = captures_piece

    def is_capture(self):
        return self.captures_piece is not None