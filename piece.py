import pygame

from constants import *

class Piece:
    def __init__(self, window, row, col, is_player = True, on_mousedown = None):
        self.window = window
        self.row = row
        self.col = col
        self.is_player = is_player
        self.hidden = False
        self.is_king = False
        self.on_mousedown = on_mousedown

    def draw(self):
        if (not self.hidden):
            center_x = self.col * CELL_WIDTH + CELL_WIDTH // 2
            center_y = self.row * CELL_HEIGHT + (CELL_HEIGHT // 2) + SCOREBOARD_HEIGHT
            pygame.draw.circle(self.window, self.get_color(), (center_x, center_y), PIECE_RADIUS)
    
    def set_position(self, row, col):
        self.row = row
        self.col = col

    def handle_event(self, event):
        if (event.type == pygame.MOUSEBUTTONDOWN and self.on_mousedown):
            x, y = event.pos
            if (self.is_player and self.contains_point(x, y)):
                self.on_mousedown(self, event)

    def contains_point(self, x, y):
        piece_x, piece_y = self.get_absolute_position()
        return (x - piece_x) ** 2 + (y - piece_y) ** 2 <= PIECE_RADIUS ** 2

    def get_absolute_position(self):
        x = self.col * CELL_WIDTH + CELL_WIDTH // 2
        y = self.row * CELL_HEIGHT + CELL_HEIGHT // 2 + SCOREBOARD_HEIGHT
        return x, y

    def get_color(self):
        if self.is_player:
            if self.is_king:
                return COLORS['player_king']
            else:
                return COLORS['red']
        else:
            if self.is_king:
                return COLORS['ai_king']
            else:
                return COLORS['black']
