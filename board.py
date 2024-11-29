import pygame
from random import choice

'''
Responsibilies: 
    1. Draw the game grid and pieces on the screen (shapes, colors)
    2. Hold the board data (array)
    3. Make moves
'''


class Board:
    def __init__(self):
        self.data = [
            [
                'black' if (row < 3 and (row + col) % 2 == 0) else
                'red' if (row > 4 and (row + col) % 2 == 0) else
                None for col in range(8)
            ]
            for row in range(8)
        ]
        self.width, self.height = 800, 800
        self.window = pygame.display.set_mode((self.width, self.height))
        self.cell_width = self.width // 8
        self.cell_height = self.height // 8
        self.padding = int(self.cell_width * 0.15)
        self.radius = (self.cell_width // 2) - self.padding
        
        self.dragging_piece = None  # Track which piece (if any) is being dragged
        self.drag_offset_x = 0  # To adjust for where the mouse grabs the piece
        self.drag_offset_y = 0
        self.dragged_piece_color = 'red'

        self.colors = {
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'white': (255, 255, 255)
        }

    def draw(self):
        self.clear()
        self.draw_grid()
        self.draw_pieces()
        self.draw_dragging_piece()

    def clear(self):
        self.window.fill((200, 200, 200))

    def draw_grid(self):
        light_color = (240, 217, 181)  # Light tan
        dark_color = (181, 136, 99)  # Darker brown

        for row in range(8):
            for col in range(8):
                rect = pygame.Rect(col * self.cell_width, row * self.cell_height, self.cell_width, self.cell_height)
                if (row + col) % 2 == 0:
                    color = light_color
                else:
                    if self.data[row][col]:  # Darker background if a piece is present
                        color = (128, 70, 27)  # Darker shade for occupied squares
                    else:
                        color = dark_color
                pygame.draw.rect(self.window, color, rect)

    def draw_pieces(self,):
        for row in range(8):
            for col in range(8):
                center_x = col * self.cell_width + self.cell_width // 2
                center_y = row * self.cell_height + self.cell_height // 2
                if self.data[row][col] == 'black':
                    pygame.draw.circle(self.window, self.colors['black'], (center_x, center_y), self.radius)
                elif self.data[row][col] == 'red':
                    pygame.draw.circle(self.window, self.colors['red'], (center_x, center_y), self.radius)

    def draw_dragging_piece(self):
        if self.dragging_piece:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            new_x = mouse_x - self.drag_offset_x
            new_y = mouse_y - self.drag_offset_y
            pygame.draw.circle(self.window,
                               self.colors[self.dragged_piece_color],
                               (new_x, new_y),
                               self.radius)

    def ai_move(self):
        ai_moves = []

        for row in range(8):
            for col in range(8):
                if self.data[row][col] == 'black':
                    potential_moves = [
                        (row + 1, col - 1),  # Forward-left
                        (row + 1, col + 1),  # Forward-right
                    ]
                    for target_row, target_col in potential_moves:
                        # Ensure within bounds and target square is empty
                        if 0 <= target_row < 8 and 0 <= target_col < 8:
                            if self.data[target_row][target_col] is None:
                                ai_moves.append(((row, col), (target_row, target_col)))

        if not ai_moves:
            print("No valid moves for AI!")
            return

        # Randomly select a valid move
        move = choice(ai_moves)
        start, end = move
        self.data[start[0]][start[1]] = None  # Remove piece from start position
        self.data[end[0]][end[1]] = 'black'  # Place piece in target position
