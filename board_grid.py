import pygame

from cell import Cell
from vector import Vector
from constants import *

class BoardGrid:
    def __init__(self, window, origin = Vector(0, 0), on_mouseup = None):
        self.window = window
        self.origin = origin
        self.on_mouseup = on_mouseup
        self.highlighted_cells = []
    
    def draw(self):
        self.draw_margin()
        self.draw_cells()
        self.draw_highlighted_cells()

    def draw_highlighted_cells(self):
        for cell in self.highlighted_cells:
            rect = pygame.Rect((cell.col * CELL_WIDTH) + self.origin.x, (cell.row * CELL_HEIGHT) + self.origin.y, CELL_WIDTH, CELL_HEIGHT)
            pygame.draw.rect(self.window, COLORS['border_color'], rect, 3)

    def draw_margin(self):
        margin_rect = pygame.Rect(self.origin.x, self.origin.y, BOARD_WIDTH, BOARD_HEIGHT)
        pygame.draw.rect(self.window, COLORS['margin_color'], margin_rect)

    def draw_cells(self):
        for row in range(NUM_ROWS):
            for col in range(NUM_COLS):
                rect = pygame.Rect((col * CELL_WIDTH) + self.origin.x, (row * CELL_HEIGHT) + self.origin.y, CELL_WIDTH, CELL_HEIGHT)
                if (row + col) % 2 == 0:
                    color = COLORS['light_color']
                else:
                    color = COLORS['dark_color']
                pygame.draw.rect(self.window, color, rect)

    def highlight_cell(self, cell):
        self.highlighted_cells.append(cell)

    def clear_highlighted_cells(self):
        self.highlighted_cells = []

    def handle_event(self, event):
        if (event.type == pygame.MOUSEBUTTONUP):
            x, y = event.pos
            point = Vector(x, y)
            if (self.point_in_grid(point)):
                self.on_mouseup(self.point_to_cell(point))
    
    def point_to_cell(self, point):
        col = (point.x - self.origin.x) // CELL_WIDTH
        row = (point.y - self.origin.y) // CELL_HEIGHT
        return Cell(row, col)

    def point_in_grid(self, point):
        return (
            self.origin.x <= point.x <= (self.origin.x + BOARD_WIDTH)
            and self.origin.y <= point.y <= (self.origin.y + BOARD_HEIGHT)
        )