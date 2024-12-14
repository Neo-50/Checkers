FRAMERATE = 60
SCOREBOARD_HEIGHT = 50
BOARD_WIDTH = 700
BOARD_HEIGHT = 700
NUM_ROWS = 8
NUM_COLS = 8
CELL_WIDTH = BOARD_WIDTH // NUM_ROWS
CELL_HEIGHT = BOARD_HEIGHT // NUM_COLS
PADDING = int(CELL_WIDTH * 0.15)
PIECE_RADIUS = (CELL_WIDTH // 2) - PADDING
COLORS = {
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'player_king': (139, 0, 0),
    'ai_king': (150, 150, 150),
    'light_color': (240, 217, 181),  # Light tan
    'dark_color': (181, 136, 99),  # Darker brown
    'border_color': (0, 255, 0),  # Green border for valid moves
    'capture_color': (255, 0, 0),
    'double_capture_color': (0, 0, 255),
    'margin_color': (150, 180, 220)
}
