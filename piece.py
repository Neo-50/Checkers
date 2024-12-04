import pygame
from constants import *

COLORS = {
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'white': (255, 255, 255),
    'blue': (0, 0, 255),
}

class Piece:
    def __init__(self, window, row, col, is_player):
        self.window = window
        self.row = row
        self.col = col
        self.is_player = is_player
        self.is_king = False
    
    def get_color(self):
        if (self.is_player):
            if (self.is_king):
                return COLORS['white']
            else:
                return COLORS['red']
        else:
            if (self.is_king):
                return COLORS['blue']
            else:
                return COLORS['black']

    def draw(self):
        center_x = self.row * CELL_WIDTH + CELL_WIDTH // 2
        center_y = self.col * CELL_HEIGHT + CELL_HEIGHT // 2
        pygame.draw.circle(self.window, self.get_color(), (center_x, center_y), PIECE_RADIUS)
