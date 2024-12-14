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
        self.possible_moves = []
        self.regular_moves = []
        self.capture_moves = []
        self.capture_pieces = []
        self.potential_double_capture_moves = []
        self.left_double_capture_move = []
        self.right_double_capture_move = []
        self.double_capture_targets = []
        self.double_capture_pieces = []

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

    def draw(self):
        center_x = self.col * CELL_WIDTH + CELL_WIDTH // 2
        center_y = self.row * CELL_HEIGHT + (CELL_HEIGHT // 2) + 50
        pygame.draw.circle(self.window, self.get_color(), (center_x, center_y), PIECE_RADIUS)
