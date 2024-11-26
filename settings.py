import pygame


class Settings:
    """A class to store all settings for checkers."""

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
        self.dragged_piece_color = 'red'

        # Initialize the board
        self.board = [
            [
                'black' if (row < 3 and (row + col) % 2 == 0) else
                'red' if (row > 4 and (row + col) % 2 == 0) else
                None for col in range(8)
            ]
            for row in range(8)
        ]

        # Set the color of the lines and gamepieces
        self.colors = {
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'white': (255, 255, 255)
        }

        # Vertical lines
        for i in range(1, 8):  # Lines 1 through 7
            start_x = i * (self.width // 8)
            setattr(self, f'vline{i}_start_x', start_x)
            setattr(self, f'vline{i}_start_y', 0)
            setattr(self, f'vline{i}_end_x', start_x)
            setattr(self, f'vline{i}_end_y', self.height)

        # Horizontal lines
        for i in range(1, 8):  # Lines 1 through 7
            start_y = i * (self.height // 8)
            setattr(self, f'hline{i}_start_x', 0)
            setattr(self, f'hline{i}_start_y', start_y)
            setattr(self, f'hline{i}_end_x', self.width)
            setattr(self, f'hline{i}_end_y', start_y)

