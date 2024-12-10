import pygame
from constants import *


class Piece:
    def __init__(self, window, row, col, is_player, hidden):
        self.window = window
        self.row = row
        self.col = col
        self.is_player = is_player
        self.hidden = hidden
        self.is_king = False
    
    def get_color(self):
        if self.is_player:
            if self.is_king:
                return COLORS['white']
            else:
                return COLORS['red']
        else:
            if self.is_king:
                return COLORS['blue']
            else:
                return COLORS['black']

    def draw(self):
        center_x = self.col * CELL_WIDTH + CELL_WIDTH // 2
        center_y = self.row * CELL_HEIGHT + CELL_HEIGHT // 2
        pygame.draw.circle(self.window, self.get_color(), (center_x, center_y), PIECE_RADIUS)
