import pygame
# from random import choice

from constants import *
from piece import Piece
from random import choice

'''
Responsibilies: 
    1. Draw the game grid and pieces on the screen (shapes, colors)
    2. Hold the board data (array)
    3. Make moves
'''


class Board:
    def __init__(self, window):
        self.window = window
        self.pieces = [
            # Computer
            Piece(self.window, 0, 0, False, False), Piece(self.window, 0, 2, False, False),
            Piece(self.window, 0, 4, False, False), Piece(self.window, 0, 6, False, False),
            Piece(self.window, 1, 1, False, False), Piece(self.window, 1, 3, False, False),
            Piece(self.window, 1, 5, False, False), Piece(self.window, 1, 7, False, False),
            Piece(self.window, 2, 0, False, False), Piece(self.window, 2, 2, False, False),
            Piece(self.window, 2, 4, False, False), Piece(self.window, 2, 6, False, False),
            # Player
            Piece(self.window, 5, 7, True, False), Piece(self.window, 5, 5, True, False),
            Piece(self.window, 5, 3, True, False), Piece(self.window, 5, 1, True, False),
            Piece(self.window, 6, 6, True, False), Piece(self.window, 6, 4, True, False),
            Piece(self.window, 6, 2, True, False), Piece(self.window, 6, 0, True, False),
            Piece(self.window, 7, 7, True, False), Piece(self.window, 7, 5, True, False),
            Piece(self.window, 7, 3, True, False), Piece(self.window, 7, 1, True, False)
        ]

        self.selected_piece = None
        self.player_turn = True
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.player_score = 0
        self.ai_score = 0

        self.possible_moves = []
        self.regular_moves = []
        self.valid_moves = []
        self.capture_moves = []
        self.capture_pieces = []

        self.delay_start_time = None
        self.waiting_to_remove = False
        self.pending_capture = None

        # Animation state variables
        self.animating_piece = None
        self.animation_start = None
        self.animation_end = None
        self.animation_progress = 0  # Progress percentage (0 to 1)
        self.animation_speed = 0.05  # Adjust for animation speed

    def update(self):
        if self.animating_piece:
            # Calculate animation progress
            self.animation_progress += self.animation_speed
            if self.animation_progress >= 1:
                self.animation_progress = 1  # Clamp to finish animation
                self.animating_piece.row, self.animating_piece.col = self.animation_end
                self.animating_piece = None  # End animation

                # If animation ends and a capture was made, continue handling it
                if self.waiting_to_remove:
                    current_time = pygame.time.get_ticks()
                    if current_time - self.delay_start_time >= 5000:  # 5-second delay
                        if self.pending_capture:
                            self.pieces.remove(self.pending_capture)
                            print(f"Piece removed: {self.pending_capture.row}, {self.pending_capture.col}")
                        self.pending_capture = None
                        self.waiting_to_remove = False
        if self.waiting_to_remove:
            current_time = pygame.time.get_ticks()
            if current_time - self.delay_start_time >= 600:
                if self.pending_capture:
                    self.pieces.remove(self.pending_capture)
                    print(f"Piece removed: {self.pending_capture.row}, {self.pending_capture.col}")
                self.pending_capture = None
                self.waiting_to_remove = False
        elif not self.player_turn:
            self.ai_move()
            self.player_turn = True

    def draw(self):
        self.clear()
        self.draw_grid()
        # Draw all pieces except the animating one
        for piece in self.pieces:
            if piece != self.animating_piece and not piece.hidden:
                piece.draw()

        # Draw the animating piece
        if self.animating_piece:
            start_x = self.animation_start[1] * CELL_WIDTH + CELL_WIDTH // 2
            start_y = (self.animation_start[0] * CELL_HEIGHT + CELL_HEIGHT // 2) + 50
            end_x = self.animation_end[1] * CELL_WIDTH + CELL_WIDTH // 2
            end_y = (self.animation_end[0] * CELL_HEIGHT + CELL_HEIGHT // 2) + 50

            # Interpolate position based on animation progress
            current_x = start_x + (end_x - start_x) * self.animation_progress
            current_y = start_y + (end_y - start_y) * self.animation_progress

            color = COLORS['blue'] if self.animating_piece.is_king else COLORS['black']
            pygame.draw.circle(self.window, color, (int(current_x), int(current_y)), PIECE_RADIUS)
        self.draw_dragging_piece()

    def clear(self):
        self.window.fill((200, 200, 200))

    def draw_grid(self):
        light_color = (240, 217, 181)  # Light tan
        dark_color = (181, 136, 99)  # Darker brown
        border_color = (0, 255, 0)  # Green border for valid moves
        capture_color = (255, 0, 0)

        for row in range(8):
            for col in range(8):
                rect = pygame.Rect(col * CELL_WIDTH, (row * CELL_HEIGHT) + 50, CELL_WIDTH, CELL_HEIGHT)
                if (row + col) % 2 == 0:
                    color = light_color
                else:
                    color = dark_color
                pygame.draw.rect(self.window, color, rect)

                # Add a border for valid moves
                if (row, col) in self.regular_moves:
                    pygame.draw.rect(self.window, border_color, rect, 3)

                if (row, col) in self.capture_moves:
                    pygame.draw.rect(self.window, capture_color, rect, 3)

    # def draw_pieces(self):
    #     for piece in self.pieces:
    #         if not piece.hidden:
    #             piece.draw()

    def find_piece(self, target_row, target_col):
        for piece in self.pieces:
            if piece.row == target_row and piece.col == target_col:
                return piece
        return None

    def handle_mousedown(self, event):
        mouse_x, mouse_y = event.pos
        row = (mouse_y - 50) // CELL_HEIGHT
        col = mouse_x // CELL_WIDTH
        radius = (CELL_WIDTH // 2) - PADDING
        print('Row: ', row, 'Col: ', col)
        for piece in self.pieces:
            piece_x = piece.col * CELL_WIDTH + CELL_WIDTH // 2
            piece_y = piece.row * CELL_HEIGHT + CELL_HEIGHT // 2 + 50
            if (piece.row == row and piece.col == col) and piece.is_player:
                if (mouse_x - piece_x) ** 2 + (mouse_y - piece_y) ** 2 <= radius ** 2:
                    # Set dragging-related attributes
                    self.selected_piece = (row, col)
                    self.drag_offset_x = mouse_x - piece_x
                    self.drag_offset_y = mouse_y - piece_y
                    self.possible_moves = [
                        (self.selected_piece[0] - 1, self.selected_piece[1] - 1),  # Top left
                        (self.selected_piece[0] - 1, self.selected_piece[1] + 1),  # Top right
                    ]
                    if piece.is_king:
                        self.possible_moves = [
                            (self.selected_piece[0] - 1, self.selected_piece[1] - 1),  # Top left
                            (self.selected_piece[0] - 1, self.selected_piece[1] + 1),  # Top right
                            (self.selected_piece[0] + 1, self.selected_piece[1] - 1),  # Top left
                            (self.selected_piece[0] + 1, self.selected_piece[1] + 1),  # Top right
                        ]
                    self.handle_move(row, col)

    def handle_move(self, row, col):
        self.capture_moves.clear()
        self.capture_pieces.clear()
        self.regular_moves.clear()
        # Check if within bounds and empty
        for move in self.possible_moves:
            target_row, target_col = move
            if 0 <= target_row < 8 and 0 <= target_col < 8:  # Check within boundaries
                target_square = self.find_piece(target_row, target_col)
                if not target_square:  # Check if empty
                    self.regular_moves.append((target_row, target_col))  # Append as tuple
                    self.valid_moves.append((target_row, target_col))

                else:
                    # Check if target square contains an opponent's piece
                    enemy_piece = self.find_piece(target_row, target_col)
                    if not enemy_piece.is_player:
                        # Calculate the landing square for a capture
                        landing_row = target_row - (row - target_row)  # Mirror target_row
                        landing_col = target_col - (col - target_col)  # Mirror target_col

                        # Ensure landing square is within bounds and empty
                        if (
                                0 <= landing_row < 8
                                and 0 <= landing_col < 8
                                and self.find_piece(landing_row, landing_col) is None
                        ):
                            self.valid_moves.append((landing_row, landing_col))  # Add to vaild moves
                            self.capture_moves.append((landing_row, landing_col))  # Add to capture moves
                            self.capture_pieces.append((target_row, target_col))  # Save opponent's piece location
                            print('Added to capture_pieces list: ', self.capture_pieces)

    def draw_dragging_piece(self):
        if self.selected_piece:
            piece = self.find_piece(self.selected_piece[0], self.selected_piece[1])
            if piece:
                if piece.is_king:
                    color = COLORS['white']
                else:
                    color = COLORS['red']
                piece.hidden = True
                mouse_x, mouse_y = pygame.mouse.get_pos()
                new_x = mouse_x - self.drag_offset_x
                new_y = mouse_y - self.drag_offset_y
                pygame.draw.circle(self.window,
                                   color,
                                   (new_x, new_y),
                                   PIECE_RADIUS)

    def handle_mouseup(self, event):
        if self.selected_piece:
            piece = self.find_piece(self.selected_piece[0], self.selected_piece[1])
            if piece:
                piece.hidden = False

            mouse_x, mouse_y = event.pos

            target_col = mouse_x // CELL_WIDTH
            target_row = (mouse_y - 50) // CELL_HEIGHT

            if (target_row, target_col) in self.regular_moves:
                # Update coords for piece object
                piece = self.find_piece(self.selected_piece[0], self.selected_piece[1])
                if piece:
                    piece.row = target_row
                    piece.col = target_col

                # King if end of board
                if target_row == 0:
                    piece.is_king = True

                self.player_turn = False

                pygame.time.wait(500)

            elif (target_row, target_col) in self.capture_moves:

                # Update coords for piece object
                piece = self.find_piece(self.selected_piece[0], self.selected_piece[1])
                if piece:
                    piece.row = target_row
                    piece.col = target_col

                # King if end of board
                if target_row == 0:
                    piece.is_king = True

                # Remove enemy piece
                if self.capture_moves and self.capture_pieces:  # Ensure lists are not empty

                    captured = False
                    for i, move in enumerate(self.capture_moves):
                        if (target_row, target_col) == move:
                            enemy_piece = self.find_piece(self.capture_pieces[i][0], self.capture_pieces[i][1])
                            if enemy_piece:
                                print(f'Enemy piece found at: {self.capture_pieces[i]}')
                                self.pieces.remove(enemy_piece)
                                print(
                                    f'Removed enemy piece at {self.capture_pieces[i][0]}, {self.capture_pieces[i][1]}')
                                captured = True
                                break

                    if not captured:
                        # Handle unexpected target_row/target_col
                        print("Error: Target square does not match any capture moves.")

                else:
                    print('Capture moves or capture pieces are empty')

                # Increase score, end turn
                self.player_score += 1
                print('Player score is now', self.player_score)

                pygame.time.wait(100)

                self.player_turn = False

        self.regular_moves = []
        self.valid_moves = []
        self.capture_moves = []
        self.capture_pieces = []
        self.selected_piece = None

    def ai_move(self):
        for row in range(8):
            for col in range(8):
                piece = self.find_piece(row, col)
                if piece:
                    if piece.is_player is False:  # Check for AI pieces
                        potential_moves = [
                            (row + 1, col - 1),  # Forward-left
                            (row + 1, col + 1),  # Forward-right
                        ]
                        if piece.is_king is True:
                            potential_moves = [
                                (row + 1, col - 1),  # Forward-left
                                (row + 1, col + 1),  # Forward-right
                                (row - 1, col - 1),  # Backward-left
                                (row - 1, col + 1),  # Backward-right
                            ]
                        for target_row, target_col in potential_moves:
                            if 0 <= target_row < 8 and 0 <= target_col < 8:  # Within boundaries

                                # Check if opponent's piece is in the target square
                                enemy_piece = self.find_piece(target_row, target_col)
                                if enemy_piece and enemy_piece.is_player:
                                    # Calculate the landing square
                                    landing_row = target_row + (target_row - row)
                                    landing_col = target_col + (target_col - col)
                                    if (
                                            0 <= landing_row < 8 and 0 <= landing_col < 8
                                            and not self.find_piece(landing_row, landing_col)
                                    ):
                                        self.capture_moves.append(
                                            ((row, col), (landing_row, landing_col), (target_row, target_col)))

                                # Check for regular moves
                                elif not self.find_piece(target_row, target_col):
                                    self.regular_moves.append(((row, col), (target_row, target_col)))

        if self.capture_moves:
            # Execute a capture (prioritized over regular moves)
            start, end, captured = choice(self.capture_moves)

            pygame.time.wait(50)

            ai_piece = self.find_piece(start[0], start[1])

            # Set up animation
            self.animating_piece = ai_piece
            self.animation_start = (ai_piece.row, ai_piece.col)
            self.animation_end = end
            self.animation_progress = 0  # Reset progress

            capture_piece = self.find_piece(captured[0], captured[1])

            if capture_piece:
                self.pending_capture = capture_piece
                self.delay_start_time = pygame.time.get_ticks()
                self.waiting_to_remove = True
            print(f"AI captures piece at {captured} by moving from {start} to {end}")

            # King if end of board
            if end[0] == 7:
                ai_piece.is_king = True
                print('AI piece is now a King!')

            self.ai_score += 1
            print('AI score is now: ', self.ai_score)
        elif self.regular_moves:
            # Execute a regular move
            start, end = choice(self.regular_moves)

            pygame.time.wait(50)

            ai_piece = self.find_piece(start[0], start[1])

            # Set up animation
            self.animating_piece = ai_piece
            self.animation_start = (ai_piece.row, ai_piece.col)
            self.animation_end = end
            self.animation_progress = 0  # Reset progress

            # King if end of board
            if end[0] == 7:
                ai_piece.is_king = True
                print('AI piece is now a King!')

        else:
            print("No valid moves for AI!")
