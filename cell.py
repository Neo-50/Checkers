

class Cell:
    def __init__(self, row, col, capture_piece = None, double_capture_piece = None):
        self.row = row
        self.col = col
        self.capture_piece = capture_piece
        self.double_capture_piece = double_capture_piece