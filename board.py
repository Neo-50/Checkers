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
        
        self.selected_piece = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.selected_piece_color = 'red'

        self.player_score = 0
        self.ai_score = 0

        self.colors = {
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'white': (255, 255, 255)
        }

    def draw(self, valid_moves):
        self.clear()
        self.draw_grid(valid_moves)
        self.draw_pieces()
        self.draw_dragging_piece()

    def clear(self):
        self.window.fill((200, 200, 200))

    def draw_grid(self, valid_moves):
        light_color = (240, 217, 181)  # Light tan
        dark_color = (181, 136, 99)  # Darker brown
        border_color = (0, 255, 0)  # Green border for valid moves

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
                # Draw the square
                pygame.draw.rect(self.window, color, rect)

                # Add a border for valid moves
                if (row, col) in valid_moves:
                    pygame.draw.rect(self.window, border_color, rect, 3)

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
        if self.selected_piece:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            new_x = mouse_x - self.drag_offset_x
            new_y = mouse_y - self.drag_offset_y
            pygame.draw.circle(self.window,
                               self.colors[self.selected_piece_color],
                               (new_x, new_y),
                               self.radius)

    def ai_move(self):
        capture_moves = []
        regular_moves = []

        for row in range(8):
            for col in range(8):
                if self.data[row][col] == 'black':  # Check for AI pieces
                    potential_moves = [
                        (row + 1, col - 1),  # Forward-left
                        (row + 1, col + 1),  # Forward-right
                    ]
                    for target_row, target_col in potential_moves:
                        if 0 <= target_row < 8 and 0 <= target_col < 8:  # Within boundaries
                            # Check if opponent's piece is in the target square
                            if self.data[target_row][target_col] == 'red':
                                # Calculate the landing square
                                landing_row = target_row + (target_row - row)
                                landing_col = target_col + (target_col - col)
                                if (
                                        0 <= landing_row < 8 and 0 <= landing_col < 8
                                        and self.data[landing_row][landing_col] is None
                                ):
                                    capture_moves.append(
                                        ((row, col), (landing_row, landing_col), (target_row, target_col)))

                            # Check for regular moves
                            elif self.data[target_row][target_col] is None:
                                regular_moves.append(((row, col), (target_row, target_col)))

        if capture_moves:
            # Execute a capture (prioritized over regular moves)
            start, end, captured = choice(capture_moves)
            print(f"AI captures piece at {captured} by moving from {start} to {end}")
            self.data[start[0]][start[1]] = None  # Remove AI piece from start
            self.data[captured[0]][captured[1]] = None  # Remove captured piece
            self.data[end[0]][end[1]] = 'black'  # Place AI piece in landing square
            self.ai_score += 1
            print('AI score is now: ', self.ai_score)
            pygame.display.flip()
        elif regular_moves:
            # Execute a regular move
            start, end = choice(regular_moves)
            print(f"AI moves from {start} to {end}")
            self.data[start[0]][start[1]] = None  # Remove AI piece from start
            self.data[end[0]][end[1]] = 'black'  # Place AI piece in target square
        else:
            print("No valid moves for AI!")

