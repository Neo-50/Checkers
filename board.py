import pygame
from random import choice

from constants import *
from piece import Piece

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

        self.regular_moves = []
        self.capture_moves = []
        self.capture_pieces = []

    def update(self):
        if (not self.player_turn):
            self.ai_move()
            self.player_turn = True

    def draw(self):
        self.clear()
        self.draw_grid()
        self.draw_scoreboard()
        self.draw_pieces()
        self.draw_selected_piece()

    def clear(self):
        self.window.fill((200, 200, 200))

    def draw_pieces(self):
        for piece in self.pieces:
            piece.draw()

    def draw_grid(self):
        margin_rect = pygame.Rect(0, 0, BOARD_WIDTH, 50)
        pygame.draw.rect(self.window, COLORS['margin_color'], margin_rect)

        for row in range(8):
            for col in range(8):
                rect = pygame.Rect(col * CELL_WIDTH, (row * CELL_HEIGHT) + 50, CELL_WIDTH, CELL_HEIGHT)
                if (row + col) % 2 == 0:
                    color = COLORS['light_color']
                else:
                    color = COLORS['dark_color']
                pygame.draw.rect(self.window, color, rect)

                # Add a border for valid moves
                if (row, col) in self.regular_moves:
                    pygame.draw.rect(self.window, COLORS['border_color'], rect, 3)

                if (row, col) in self.capture_moves:
                    pygame.draw.rect(self.window, COLORS['capture_color'], rect, 3)


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

    def find_piece(self, row, col):
        for piece in self.pieces:
            if piece.row == row and piece.col == col:
                return piece
        return None

    def handle_mousedown(self, event):
        if not self.player_turn:
            return
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
                    self.do_player_move(piece)

    def find_possible_player_moves(self, piece):
        if piece.is_king:
            return [
                (piece.row - 1, piece.col - 1),  # Top left
                (piece.row - 1, piece.col + 1),  # Top right
                (piece.row + 1, piece.col - 1),  # Bottom left
                (piece.row + 1, piece.col + 1),  # Bottom right
            ]
        else:
            return [
                (piece.row - 1, piece.col - 1),  # Top left
                (piece.row - 1, piece.col + 1),  # Top right
            ]

    def do_player_move(self, piece):
        self.regular_moves.clear()
        self.capture_moves.clear()
        self.capture_pieces.clear()
        
        # Check if within bounds and empty
        for i, move in enumerate(self.find_possible_player_moves(piece)):
            target_row, target_col = move
            if self.cell_is_in_board(target_row, target_col):
                target_piece = self.find_piece(target_row, target_col)  # Check for opponent piece
                if not target_piece:  # Check if empty
                    self.regular_moves.append((target_row, target_col))  # Append as tuple
                else:
                    enemy_piece = self.find_piece(target_row, target_col)
                    if not enemy_piece.is_player:  # Filter player pieces
                        # SAVE ENEMY PIECE LOCATION
                        self.capture_pieces.append((target_row, target_col, i))

                        # Calculate the landing square for a capture
                        landing_row = target_row - (piece.row - target_row)  # Mirror target_row
                        landing_col = target_col - (piece.col - target_col)  # Mirror target_col

                        # Ensure landing square is within bounds and empty
                        if (
                            self.cell_is_in_board(landing_row, landing_col) and
                            self.find_piece(landing_row, landing_col) is None
                        ):
                            self.capture_moves.append((landing_row, landing_col))  # Add to capture moves

    def cell_is_in_board(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def draw_selected_piece(self):
        if not self.selected_piece:
            return
        self.selected_piece.hidden = True
        mouse_x, mouse_y = pygame.mouse.get_pos()
        new_x = mouse_x - self.drag_offset_x
        new_y = mouse_y - self.drag_offset_y
        pygame.draw.circle(self.window, self.selected_piece.get_color(), (new_x, new_y), PIECE_RADIUS)

    def handle_mouseup(self, event):
        if not self.player_turn:
            return
        if self.selected_piece:
            self.selected_piece.hidden = False  # Make piece visible again

            mouse_x, mouse_y = event.pos

            target_col = mouse_x // CELL_WIDTH
            target_row = (mouse_y - 50) // CELL_HEIGHT

            # INITIATE REGULAR MOVE
            if (target_row, target_col) in self.regular_moves:

                # Update attributes for piece object
                self.selected_piece.row = target_row
                self.selected_piece.col = target_col

                print('Player moved to ', target_row, target_col)

                # King if end of board
                if target_row == 0:
                    self.selected_piece.is_king = True

                self.player_turn = False

            # INITIATE CAPTURE MOVE
            elif (target_row, target_col) in self.capture_moves:

                # Update attributes to move the piece object
                self.selected_piece.row = target_row
                self.selected_piece.col = target_col

                # King if end of board
                if target_row == 0:
                    self.selected_piece.is_king = True

                # Remove enemy piece
                if self.capture_moves and self.capture_pieces:  # Ensure lists are not empty
                    captured = False
                    for i, move in enumerate(self.capture_moves):
                        if (target_row, target_col) == move:
                            enemy_piece = self.find_piece(self.capture_pieces[i][0], self.capture_pieces[i][1])
                            if enemy_piece:
                                self.pieces.remove(enemy_piece)
                                print(f'Piece removed: ({enemy_piece.row}, {enemy_piece.col})')
                                captured = True
                                break
                    if not captured:
                        # Handle unexpected target_row/target_col
                        print("Error: Target square does not match any capture moves.")
                else:
                    print('Error: Capture moves or capture pieces are empty')

                self.player_score += 1
                self.player_turn = False

            else:
                print('Error: Moves list is empty or target square does not match moves list')

        self.regular_moves.clear()
        self.capture_moves.clear()
        self.capture_pieces.clear()
        self.selected_piece = None

    def ai_move(self):
        print('ai_move')
        for row in range(8):
            for col in range(8):
                piece = self.find_piece(row, col)
                if piece and not piece.is_player:
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

            ai_piece = self.find_piece(start[0], start[1])

            capture_piece = self.find_piece(captured[0], captured[1])
            self.pieces.remove(capture_piece)
            ai_piece.set_position(end[0], end[1])

            # King if end of board
            if end[0] == 7:
                ai_piece.is_king = True

            self.ai_score += 1

        elif self.regular_moves:
            # Execute a regular move
            start, end = choice(self.regular_moves)

            ai_piece = self.find_piece(start[0], start[1])
            ai_piece.set_position(end[0], end[1])

            # King if end of board
            if end[0] == 7:
                ai_piece.is_king = True

        else:
            print("No valid moves for AI!")
