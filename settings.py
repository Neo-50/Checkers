import pygame


class Settings:
    """A class to store all settings for Tic Tac Toe Graphical."""

    def __init__(self):
        """Initialize the game's static settings."""

        # Set the dimensions of the window
        self.width, self.height = 800, 800

        # Create the window
        self.window = pygame.display.set_mode((self.width, self.height))

        # Define cell width and height
        self.cell_width = self.width // 8
        self.cell_height = self.height // 8

        # Define padding
        self.padding = int(self.cell_width * 0.15)

        # Define game-piece radius
        self.radius = (self.cell_width // 2) - self.padding

        # Define dragging variables
        self.dragging_piece = None  # Track which piece (if any) is being dragged
        self.drag_offset_x = 0  # To adjust for where the mouse grabs the piece
        self.drag_offset_y = 0

        # Grid state: 3x3 matrix to track Xs and Os
        self.board = [
            ['black' for _ in range(8)] if row < 2 else
            ['red' for _ in range(8)] if row > 5 else
            [None for _ in range(8)]
            for row in range(8)
        ]

        # Set the color of the lines and gamepieces
        self.colors = {
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'white': (255, 255, 255)
        }
        # Vertical lines
        self.vline1_start_x, self.vline1_start_y = self.width // 8, 0
        self.vline1_end_x, self.vline1_end_y = self.width // 8, self.height

        self.vline2_start_x, self.vline2_start_y = 2 * (self.width // 8), 0
        self.vline2_end_x, self.vline2_end_y = 2 * (self.width // 8), self.height

        self.vline3_start_x, self.vline3_start_y = 3 * (self.width // 8), 0
        self.vline3_end_x, self.vline3_end_y = 3 * (self.width // 8), self.height

        self.vline4_start_x, self.vline4_start_y = 4 * (self.width // 8), 0
        self.vline4_end_x, self.vline4_end_y = 4 * (self.width // 8), self.height

        self.vline5_start_x, self.vline5_start_y = 5 * (self.width // 8), 0
        self.vline5_end_x, self.vline5_end_y = 5 * (self.width // 8), self.height

        self.vline6_start_x, self.vline6_start_y = 6 * (self.width // 8), 0
        self.vline6_end_x, self.vline6_end_y = 6 * (self.width // 8), self.height

        self.vline7_start_x, self.vline7_start_y = 7 * (self.width // 8), 0
        self.vline7_end_x, self.vline7_end_y = 7 * (self.width // 8), self.height

        # Horizontal lines
        self.hline1_start_x, self.hline1_start_y = 0, self.height // 8
        self.hline1_end_x, self.hline1_end_y = self.width, self.height // 8

        self.hline2_start_x, self.hline2_start_y = 0, 2 * (self.height // 8)
        self.hline2_end_x, self.hline2_end_y = self.width, 2 * (self.height // 8)

        self.hline3_start_x, self.hline3_start_y = 0, 3 * (self.height // 8)
        self.hline3_end_x, self.hline3_end_y = self.width, 3 * (self.height // 8)

        self.hline4_start_x, self.hline4_start_y = 0, 4 * (self.height // 8)
        self.hline4_end_x, self.hline4_end_y = self.width, 4 * (self.height // 8)

        self.hline5_start_x, self.hline5_start_y = 0, 5 * (self.height // 8)
        self.hline5_end_x, self.hline5_end_y = self.width, 5 * (self.height // 8)

        self.hline6_start_x, self.hline6_start_y = 0, 6 * (self.height // 8)
        self.hline6_end_x, self.hline6_end_y = self.width, 6 * (self.height // 8)

        self.hline7_start_x, self.hline7_start_y = 0, 7 * (self.height // 8)
        self.hline7_end_x, self.hline7_end_y = self.width, 7 * (self.height // 8)
