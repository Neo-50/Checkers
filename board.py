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

        self.ai_regular_moves = []
        self.ai_capture_moves = []

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
                            print(f"Piece removed: ({self.pending_capture.row}, {self.pending_capture.col})")
                        self.pending_capture = None
                        self.waiting_to_remove = False
        if self.waiting_to_remove:
            current_time = pygame.time.get_ticks()
            if current_time - self.delay_start_time >= 600:
                if self.pending_capture:
                    self.pieces.remove(self.pending_capture)
                    print(f"Piece removed: ({self.pending_capture.row}, {self.pending_capture.col})")
                self.pending_capture = None
                self.waiting_to_remove = False
        elif not self.player_turn:
            self.ai_move()
            self.player_turn = True

    def draw(self):
        self.clear()
        self.draw_grid()
        self.draw_scoreboard()
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

            color = COLORS['ai_king'] if self.animating_piece.is_king else COLORS['black']
            pygame.draw.circle(self.window, color, (int(current_x), int(current_y)), PIECE_RADIUS)
        self.draw_dragging_piece()

    def clear(self):
        self.window.fill((200, 200, 200))

    def draw_grid(self):
        light_color = (240, 217, 181)  # Light tan
        dark_color = (181, 136, 99)  # Darker brown
        border_color = (0, 255, 0)  # Green border for valid moves
        capture_color = (255, 0, 0)
        double_capture_color = (0, 0, 255)
        margin_color = (150, 180, 220)

        margin_rect = pygame.Rect(0, 0, BOARD_WIDTH, 50)
        pygame.draw.rect(self.window, margin_color, margin_rect)

        piece = self.selected_piece

        for row in range(8):
            for col in range(8):
                rect = pygame.Rect(col * CELL_WIDTH, (row * CELL_HEIGHT) + 50, CELL_WIDTH, CELL_HEIGHT)
                if (row + col) % 2 == 0:
                    color = light_color
                else:
                    color = dark_color
                pygame.draw.rect(self.window, color, rect)

                # Add a border for valid moves
                if piece:
                    if (row, col) in piece.regular_moves:
                        pygame.draw.rect(self.window, border_color, rect, 3)

                    if (row, col) in piece.capture_moves:
                        pygame.draw.rect(self.window, capture_color, rect, 3)

                    if (row, col) in piece.double_capture_moves:
                        pygame.draw.rect(self.window, double_capture_color, rect, 3)

    def draw_scoreboard(self):
        font = pygame.font.SysFont('Arial', 20)
        text_color = (0, 0, 0)  # Black color for the text

        score_text = font.render(f'Player: {self.player_score}    |    AI: {self.ai_score}', True, text_color)
        title_text = font.render('Checkers', True, text_color)

        score_text_width = score_text.get_width()

        score_text_x = self.window.get_width() - score_text_width - 10
        score_text_y = 10

        self.window.blit(score_text, (score_text_x, score_text_y))
        self.window.blit(title_text, (10, score_text_y))

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
        for piece in self.pieces:
            piece_x = piece.col * CELL_WIDTH + CELL_WIDTH // 2
            piece_y = piece.row * CELL_HEIGHT + CELL_HEIGHT // 2 + 50
            if (piece.row == row and piece.col == col) and piece.is_player:
                if (mouse_x - piece_x) ** 2 + (mouse_y - piece_y) ** 2 <= radius ** 2:
                    # Set dragging-related attributes
                    self.selected_piece = piece
                    self.drag_offset_x = mouse_x - piece_x
                    self.drag_offset_y = mouse_y - piece_y
                    piece.possible_moves = [
                        (self.selected_piece.row - 1, self.selected_piece.col - 1),  # Top left
                        (self.selected_piece.row - 1, self.selected_piece.col + 1),  # Top right
                    ]
                    if piece.is_king:
                        piece.possible_moves = [
                            (self.selected_piece.row - 1, self.selected_piece.col - 1),  # Top left
                            (self.selected_piece.row - 1, self.selected_piece.col + 1),  # Top right
                            (self.selected_piece.row + 1, self.selected_piece.col - 1),  # Bottom left
                            (self.selected_piece.row + 1, self.selected_piece.col + 1),  # Bottom right
                        ]
                    self.handle_move(row, col, piece)

    def handle_move(self, row, col, piece):

        piece.regular_moves.clear()
        piece.capture_moves.clear()
        piece.capture_pieces.clear()
        piece.double_capture_moves.clear()
        piece.double_capture_targets.clear()
        piece.potential_double_capture_moves.clear()
        piece.double_capture_pieces.clear()

        for move in piece.possible_moves:
            target_row, target_col = move
            if 0 <= target_row < 8 and 0 <= target_col < 8:  # CHECK BOUNDARIES
                check_piece = self.find_piece(target_row, target_col)  # CHECK FOR ENEMY PIECE
                if not check_piece:  # Check if empty
                    piece.regular_moves.append((target_row, target_col))  # Append as tuple
                else:
                    enemy_piece = check_piece
                    if not enemy_piece.is_player:  # Filter player pieces
                        # SAVE ENEMY PIECE LOCATION
                        piece.capture_pieces.append((target_row, target_col))

                        # Calculate the landing square for a capture
                        landing_row = target_row - (row - target_row)  # Mirror target_row
                        landing_col = target_col - (col - target_col)  # Mirror target_col

                        # CHECK BOUNDARIES AND EMPTY
                        if (
                                0 <= landing_row < 8
                                and 0 <= landing_col < 8
                                and self.find_piece(landing_row, landing_col) is None
                        ):
                            piece.capture_moves.append((landing_row, landing_col))  # Add to capture moves
        self.check_double_captures(piece)

    def check_double_captures(self, piece):
        if piece.capture_moves:
            #  LANDING SQUARE FROM THE FIRST CAPTURE BRANCHES INTO 2 SQUARES
            #  POTENTIALLY CONTAINING OPPONENT PIECES
            piece.potential_double_capture_moves.extend([
                (piece.capture_moves[0][0] - 1, piece.capture_moves[0][1] - 1),  # Top left
                (piece.capture_moves[0][0] - 1, piece.capture_moves[0][1] + 1)  # Top right
            ])
            if piece.is_king:
                piece.potential_double_capture_moves.extend([
                    (piece.capture_moves[0][0] - 1, piece.capture_moves[0][1] - 1),  # Top left
                    (piece.capture_moves[0][0] - 1, piece.capture_moves[0][1] + 1),  # Top right
                    (piece.capture_moves[0][0] + 1, piece.capture_moves[0][1] - 1),  # Bottom left
                    (piece.capture_moves[0][0] + 1, piece.capture_moves[0][1] + 1)  # Bottom right
                ])

        if len(piece.capture_moves) > 1:
            piece.potential_double_capture_moves.extend([
                (piece.capture_moves[1][0] - 1, piece.capture_moves[1][1] - 1),  # Top left
                (piece.capture_moves[1][0] - 1, piece.capture_moves[1][1] + 1)  # Top right
            ])
            if piece.is_king:
                piece.potential_double_capture_moves.extend([
                    (piece.capture_moves[1][0] - 1, piece.capture_moves[1][1] - 1),  # Top left
                    (piece.capture_moves[1][0] - 1, piece.capture_moves[1][1] + 1),  # Top right
                    (piece.capture_moves[1][0] + 1, piece.capture_moves[1][1] - 1),  # Bottom left
                    (piece.capture_moves[1][0] + 1, piece.capture_moves[1][1] + 1)  # Bottom right
                ])
        piece.double_capture_targets = [
            i for i in piece.potential_double_capture_moves if all(8 > j > 0 for j in i)  # CHECK BOUNDARIES
        ]
        for i, j in enumerate(piece.double_capture_targets):
            enemy_piece = self.find_piece(j[0], j[1])
            if enemy_piece and not enemy_piece.is_player:  # Check if squares contain an opponent piece
                # SAVE SECOND ENEMY PIECE LOCATION
                piece.double_capture_pieces.append((enemy_piece.row, enemy_piece.col))
                print(f'Double capture pieces: {piece.double_capture_pieces}')

        self.find_double_landing_squares(piece)

    def find_double_landing_squares(self, piece):
        for i, j in enumerate(piece.capture_moves):
            # CALCULATE LEFT LANDING SQUARE
            landing_row = j[0] - 2
            landing_col = j[1] - 2
            if 8 > landing_row >= 0 and 8 > landing_col >= 0:  # CHECK BOUNDARIES
                landing_check = self.find_piece(landing_row, landing_col)  # CHECK EMPTY
                if not landing_check:
                    check_piece = self.find_piece(landing_row + 1, landing_col + 1)
                    if check_piece:
                        piece.double_capture_moves.append((landing_row, landing_col))

            # CALCULATE RIGHT LANDING SQUARE
            landing_row = j[0] - 2
            landing_col = j[1] + 2
            if 8 > landing_row >= 0 and 8 > landing_col >= 0:  # CHECK BOUNDARIES
                landing_check = self.find_piece(landing_row, landing_col)  # CHECK EMPTY
                if not landing_check:
                    check_piece = self.find_piece(landing_row + 1, landing_col - 1)
                    if check_piece:
                        piece.double_capture_moves.append((landing_row, landing_col))
            if piece.is_king:
                # CALCULATE BOTTOM LEFT LANDING SQUARE
                landing_row = j[0] + 2
                landing_col = j[1] - 2
                if 8 > landing_row >= 0 and 8 > landing_col >= 0:  # CHECK BOUNDARIES
                    landing_check = self.find_piece(landing_row, landing_col)  # CHECK EMPTY
                    if not landing_check:
                        check_piece = self.find_piece(landing_row + 1, landing_col - 1)
                        if check_piece:
                            piece.double_capture_moves.append((landing_row, landing_col))
                # CALCULATE BOTTOM RIGHT LANDING SQUARE
                landing_row = j[0] + 2
                landing_col = j[1] + 2
                if 8 > landing_row >= 0 and 8 > landing_col >= 0:  # CHECK BOUNDARIES
                    landing_check = self.find_piece(landing_row, landing_col)  # CHECK EMPTY
                    if not landing_check:
                        check_piece = self.find_piece(landing_row + 1, landing_col + 1)
                        if check_piece:
                            piece.double_capture_moves.append((landing_row, landing_col))

    def draw_dragging_piece(self):
        if self.selected_piece:
            piece = self.selected_piece
            if piece:
                if piece.is_king:
                    color = COLORS['player_king']
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
            piece = self.selected_piece
            if piece:
                piece.hidden = False  # Make piece visible again

            mouse_x, mouse_y = event.pos

            target_col = mouse_x // CELL_WIDTH
            target_row = (mouse_y - 50) // CELL_HEIGHT

            # INITIATE REGULAR MOVE
            if (target_row, target_col) in piece.regular_moves:

                # Update attributes for piece object
                piece.row = target_row
                piece.col = target_col

                print('Player moved to ', target_row, target_col)

                # King if end of board
                if target_row == 0:
                    piece.is_king = True

                self.selected_piece = None
                self.player_turn = False

            # INITIATE CAPTURE MOVE
            elif (target_row, target_col) in piece.capture_moves:

                # Update attributes to move the piece object
                piece.row = target_row
                piece.col = target_col

                # King if end of board
                if target_row == 0:
                    piece.is_king = True

                # Remove enemy piece
                self.remove_single_piece(piece)

                self.selected_piece = None

            # INITIATE DOUBLE CAPTURE MOVE
            elif (target_row, target_col) in piece.double_capture_moves:

                # Get the starting position
                piece_start = (piece.row, piece.col)

                # Update attributes to move the piece object
                piece.row = target_row
                piece.col = target_col

                if target_row == 0:
                    piece.is_king = True
                if piece.is_king:
                    self.remove_double_pieces_king(piece, piece_start)
                else:
                    self.remove_double_pieces(piece, piece_start)

                self.selected_piece = None

            piece.double_capture_pieces.clear()
            piece.regular_moves.clear()
            piece.capture_moves.clear()
            piece.capture_pieces.clear()
            piece.double_capture_moves.clear()
            piece.double_capture_targets.clear()
            piece.potential_double_capture_moves.clear()
        self.selected_piece = None

    def remove_single_piece(self, piece):
        if piece.capture_moves and piece.capture_pieces:  # Ensure lists are not empty

            for i, capture_piece in enumerate(piece.capture_pieces):
                if piece.col - 1 == capture_piece[1]:
                    remove_piece = self.find_piece(capture_piece[0], capture_piece[1])
                    self.pieces.remove(remove_piece)
                    print(f'Left piece removed: ({remove_piece.row}, {remove_piece.col})')
                    self.player_score += 1
                    self.player_turn = False
                    break
                elif piece.col + 1 == capture_piece[1]:
                    remove_piece = self.find_piece(capture_piece[0], capture_piece[1])
                    self.pieces.remove(remove_piece)
                    print(f'Right piece removed: ({remove_piece.row}, {remove_piece.col})')
                    self.player_score += 1
                    self.player_turn = False
                    break
            else:
                print('Unable to find capture piece!')
                print(piece.capture_pieces)
        else:
            print('Error: Capture moves or capture pieces are empty')

    def remove_double_pieces(self, piece, piece_start):
        if piece.col + 4 == piece_start[1]:
            remove_piece1 = self.find_piece(piece.row + 1, piece.col + 1)
            remove_piece2 = self.find_piece(piece_start[0] - 1, piece_start[1] - 1)
            if remove_piece1 and remove_piece2:
                self.pieces.remove(remove_piece1)
                self.pieces.remove(remove_piece2)
                self.player_score += 2
                self.player_turn = False
        if piece.col == piece_start[1]:
            check_left_landing = self.find_piece(piece_start[0] - 2, piece_start[1] - 2)
            if piece_start[1] - 2 >= 0:
                if not check_left_landing:
                    remove_piece1 = self.find_piece(piece.row + 1, piece.col - 1)
                    remove_piece2 = self.find_piece(piece_start[0] - 1, piece_start[1] - 1)
                    if remove_piece1 and remove_piece2:
                        self.pieces.remove(remove_piece1)
                        self.pieces.remove(remove_piece2)
                        self.player_score += 2
                        self.player_turn = False
        if piece.col == piece_start[1]:
            check_right_landing = self.find_piece(piece_start[0] - 2, piece_start[1] + 2)
            if piece_start[1] + 2 <= 7:
                if not check_right_landing:
                    remove_piece1 = self.find_piece(piece.row + 1, piece.col + 1)
                    remove_piece2 = self.find_piece(piece_start[0] - 1, piece_start[1] + 1)
                    if remove_piece1 and remove_piece2:
                        self.pieces.remove(remove_piece1)
                        self.pieces.remove(remove_piece2)
                        self.player_score += 2
                        self.player_turn = False
        if piece.col - 4 == piece_start[1]:
            remove_piece1 = self.find_piece(piece.row + 1, piece.col - 1)
            remove_piece2 = self.find_piece(piece_start[0] - 1, piece_start[1] + 1)
            if remove_piece1 and remove_piece2:
                self.pieces.remove(remove_piece1)
                self.pieces.remove(remove_piece2)
                self.player_score += 2
                self.player_turn = False

    def remove_double_pieces_king(self, piece, piece_start):
        # Left straight capture
        if piece.col + 4 == piece_start[1]:
            remove_piece1 = self.find_piece(piece.row + 1, piece.col + 1)
            remove_piece2 = self.find_piece(piece_start[0] - 1, piece_start[1] - 1)
            if remove_piece1 and remove_piece2:
                self.pieces.remove(remove_piece1)
                self.pieces.remove(remove_piece2)
                self.player_score += 2
                self.player_turn = False
        # Left-right zigzag capture
        if piece.col == piece_start[1]:
            check_left_landing = self.find_piece(piece_start[0] - 2, piece_start[1] - 2)
            if piece_start[1] - 2 >= 0:
                if not check_left_landing:
                    remove_piece1 = self.find_piece(piece.row + 1, piece.col - 1)
                    remove_piece2 = self.find_piece(piece_start[0] - 1, piece_start[1] - 1)
                    if remove_piece1 and remove_piece2:
                        self.pieces.remove(remove_piece1)
                        self.pieces.remove(remove_piece2)
                        self.player_score += 2
                        self.player_turn = False
        # Right-left zigzag capture
        if piece.col == piece_start[1]:
            check_right_landing = self.find_piece(piece_start[0] - 2, piece_start[1] + 2)
            if piece_start[1] + 2 <= 7:
                if not check_right_landing:
                    remove_piece1 = self.find_piece(piece.row + 1, piece.col + 1)
                    remove_piece2 = self.find_piece(piece_start[0] - 1, piece_start[1] + 1)
                    if remove_piece1 and remove_piece2:
                        self.pieces.remove(remove_piece1)
                        self.pieces.remove(remove_piece2)
                        self.player_score += 2
                        self.player_turn = False
        # Right straight capture
        if piece.col - 4 == piece_start[1]:
            remove_piece1 = self.find_piece(piece.row + 1, piece.col - 1)
            remove_piece2 = self.find_piece(piece_start[0] - 1, piece_start[1] + 1)
            if remove_piece1 and remove_piece2:
                self.pieces.remove(remove_piece1)
                self.pieces.remove(remove_piece2)
                self.player_score += 2
                self.player_turn = False
        # Bottom left straight capture
        if piece.col + 4 == piece_start[1]:
            remove_piece1 = self.find_piece(piece.row - 1, piece.col + 1)
            remove_piece2 = self.find_piece(piece_start[0] + 1, piece_start[1] - 1)
            if remove_piece1 and remove_piece2:
                self.pieces.remove(remove_piece1)
                self.pieces.remove(remove_piece2)
                self.player_score += 2
                self.player_turn = False
        # Bottom left-right zigzag capture
        if piece.col == piece_start[1]:
            check_left_landing = self.find_piece(piece_start[0] - 2, piece_start[1] - 2)
            if piece_start[1] - 2 >= 0:
                if not check_left_landing:
                    remove_piece1 = self.find_piece(piece.row - 1, piece.col - 1)
                    remove_piece2 = self.find_piece(piece_start[0] + 1, piece_start[1] - 1)
                    if remove_piece1 and remove_piece2:
                        self.pieces.remove(remove_piece1)
                        self.pieces.remove(remove_piece2)
                        self.player_score += 2
                        self.player_turn = False
        # Bottom right-left zigzag capture
        if piece.col == piece_start[1]:
            check_right_landing = self.find_piece(piece_start[0] - 2, piece_start[1] + 2)
            if piece_start[1] + 2 <= 7:
                if not check_right_landing:
                    remove_piece1 = self.find_piece(piece.row - 1, piece.col + 1)
                    remove_piece2 = self.find_piece(piece_start[0] + 1, piece_start[1] + 1)
                    if remove_piece1 and remove_piece2:
                        self.pieces.remove(remove_piece1)
                        self.pieces.remove(remove_piece2)
                        self.player_score += 2
                        self.player_turn = False
        # Right straight capture
        if piece.col - 4 == piece_start[1]:
            remove_piece1 = self.find_piece(piece.row - 1, piece.col - 1)
            remove_piece2 = self.find_piece(piece_start[0] + 1, piece_start[1] + 1)
            if remove_piece1 and remove_piece2:
                self.pieces.remove(remove_piece1)
                self.pieces.remove(remove_piece2)
                self.player_score += 2
                self.player_turn = False

    def ai_move(self):
        self.ai_regular_moves.clear()
        self.ai_capture_moves.clear()
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
                                        self.ai_capture_moves.append(
                                            ((row, col), (landing_row, landing_col), (target_row, target_col)))

                                # Check for regular moves
                                elif not self.find_piece(target_row, target_col):
                                    self.ai_regular_moves.append(((row, col), (target_row, target_col)))

        if self.ai_capture_moves:
            # Execute a capture (prioritized over regular moves)
            start, end, captured = choice(self.ai_capture_moves)

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

            # King if end of board
            if end[0] == 7:
                ai_piece.is_king = True

            self.ai_score += 1

        elif self.ai_regular_moves:
            # Execute a regular move
            start, end = choice(self.ai_regular_moves)

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

        else:
            print("No valid moves for AI!")
