
BOARD_WIDTH = 800
BOARD_HEIGHT = 800
CELL_WIDTH = BOARD_WIDTH // 8
CELL_HEIGHT = BOARD_HEIGHT // 8
PADDING = int(CELL_WIDTH * 0.15)
PIECE_RADIUS = (CELL_WIDTH // 2) - PADDING
COLORS = {
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'white': (255, 255, 255),
    'blue': (0, 0, 255),
}
