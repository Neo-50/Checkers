import pygame

from constants import *
from vector import Vector
from cell import Cell


class Piece:
    def __init__(self, window, position: Cell, is_player: bool = True, on_mousedown=None):
        self.window = window
        self.position = position
        self.is_player = is_player
        self.hidden = False
        self.is_king = False
        self.on_mousedown = on_mousedown

    def __eq__(self, other):
        return self.position == other.position

    def draw(self):
        if not self.hidden:
            pygame.draw.circle(self.window, self.get_color(), self.get_absolute_position().tuple(), PIECE_RADIUS)
    
    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False

    def set_position(self, position: Cell):
        self.position = position

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.on_mousedown:
            if self.is_player and self.contains_point(Vector(event.pos[0], event.pos[1])):
                self.on_mousedown(self, event)

    def contains_point(self, point):
        position = self.get_absolute_position()
        return (point.x - position.x) ** 2 + (point.y - position.y) ** 2 <= PIECE_RADIUS ** 2

    def get_absolute_position(self):
        x = self.position.col * CELL_WIDTH + CELL_WIDTH // 2
        y = self.position.row * CELL_HEIGHT + CELL_HEIGHT // 2 + SCOREBOARD_HEIGHT
        return Vector(x, y)

    def promote(self):
        self.is_king = True

    def get_adjacent_cells(self):
        y_dir = 1 if self.is_player else -1  # Invert y if we're a computer piece
        adjacents = [
            Cell(self.position.row - y_dir, self.position.col - 1),
            Cell(self.position.row - y_dir, self.position.col + 1)
        ]
        if self.is_king:
            adjacents.append(Cell(self.position.row + y_dir, self.position.col - 1))
            adjacents.append(Cell(self.position.row + y_dir, self.position.col + 1))
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
