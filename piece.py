import pygame

from constants import *
from vector import Vector
from cell import Cell

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
            pygame.draw.circle(self.window, self.get_color(), self.get_absolute_position().tuple(), PIECE_RADIUS)
    
    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def handle_event(self, event):
        if (event.type == pygame.MOUSEBUTTONDOWN and self.on_mousedown):
            if (self.is_player and self.contains_point(Vector(event.pos[0], event.pos[1]))):
                self.on_mousedown(self, event)

    def contains_point(self, point):
        position = self.get_absolute_position()
        return (point.x - position.x) ** 2 + (point.y - position.y) ** 2 <= PIECE_RADIUS ** 2

    def get_absolute_position(self):
        x = self.col * CELL_WIDTH + CELL_WIDTH // 2
        y = self.row * CELL_HEIGHT + CELL_HEIGHT // 2 + SCOREBOARD_HEIGHT
        return Vector(x, y)

    def promote(self):
        self.is_king = True

    def get_adjacent_cells(self):
        adjacents = [
            Cell(self.row - 1, self.col - 1),  # Top left
            Cell(self.row - 1, self.col + 1),  # Top right
        ]
        if self.is_king:
            adjacents.append(Cell(self.row + 1, self.col - 1))   # Bottom left
            adjacents.append(Cell(self.row + 1, self.col + 1))   # Bottom right
        return adjacents

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
