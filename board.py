import pygame
# from random import choice

from constants import *
from piece import Piece
from cell import Cell
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
                            # print(f"Piece removed: ({self.pending_capture.row}, {self.pending_capture.col})")
                        self.pending_capture = None
                        self.waiting_to_remove = False
        if self.waiting_to_remove:
            current_time = pygame.time.get_ticks()
            if current_time - self.delay_start_time >= 600:
                if self.pending_capture:
                    self.pieces.remove(self.pending_capture)
                    # print(f"Piece removed: ({self.pending_capture.row}, {self.pending_capture.col})")
                self.pending_capture = None
                self.waiting_to_remove = False
        elif not self.player_turn:
            self.ai_move()
            self.player_turn = True

    def draw(self):
        self.window.fill((200, 200, 200))
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


    def draw_grid(self):
        light_color = (240, 217, 181)  # Light tan
        dark_color = (181, 136, 99)  # Darker brown

        margin_color = (150, 180, 220)

        margin_rect = pygame.Rect(0, 0, BOARD_WIDTH, SCOREBOARD_HEIGHT)
        pygame.draw.rect(self.window, margin_color, margin_rect)

        for row in range(8):
            for col in range(8):
                rect = pygame.Rect(col * CELL_WIDTH, (row * CELL_HEIGHT) + 50, CELL_WIDTH, CELL_HEIGHT)
                if (row + col) % 2 == 0:
                    color = light_color
                else:
                    color = dark_color
                pygame.draw.rect(self.window, color, rect)
        self.draw_highlighted_cells()


    def draw_highlighted_cells(self):
        if self.selected_piece:
            for cell in self.selected_piece.candidate_moves:
                rect = pygame.Rect((cell.col * CELL_WIDTH),
                (cell.row * CELL_HEIGHT) + SCOREBOARD_HEIGHT,
                CELL_WIDTH, CELL_HEIGHT)
                pygame.draw.rect(self.window, COLORS['border_color'], rect, 3)
            for cell in self.selected_piece.capture_moves:
                rect = pygame.Rect((cell.col * CELL_WIDTH),
                (cell.row * CELL_HEIGHT) + SCOREBOARD_HEIGHT,
                CELL_WIDTH, CELL_HEIGHT)
                pygame.draw.rect(self.window, COLORS['capture_color'], rect, 3)
            for cell in self.selected_piece.double_captures:
                rect = pygame.Rect((cell.col * CELL_WIDTH),
                (cell.row * CELL_HEIGHT) + SCOREBOARD_HEIGHT,
                CELL_WIDTH, CELL_HEIGHT)
                pygame.draw.rect(self.window, COLORS['double_capture_color'], rect, 3)


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
        self.set_drag_attributes(event)
        self.find_candidate_moves()
        self.check_double_captures()
    
    def set_drag_attributes(self, event):
        self.selected_piece = None
        mouse_x, mouse_y = event.pos
        row = (mouse_y - 50) // CELL_HEIGHT
        col = mouse_x // CELL_WIDTH
        radius = (CELL_WIDTH // 2) - PADDING
        for piece in self.pieces:
            piece_x = piece.col * CELL_WIDTH + CELL_WIDTH // 2
            piece_y = piece.row * CELL_HEIGHT + CELL_HEIGHT // 2 + 50
            if (piece.row == row and piece.col == col) and piece.is_player:
                if (mouse_x - piece_x) ** 2 + (mouse_y - piece_y) ** 2 <= radius ** 2:

                    self.selected_piece = piece
                    piece.candidate_moves.clear()
                    piece.capture_moves.clear()
                    piece.double_captures.clear()

                    self.drag_offset_x = mouse_x - piece_x
                    self.drag_offset_y = mouse_y - piece_y


    @staticmethod
    def in_boundaries(row, col):
        return 0 <= row < NUM_ROWS and 0 <= col < NUM_COLS


    def find_candidate_moves(self):
        if not self.selected_piece:
            return
        if self.selected_piece:
            piece = self.selected_piece
            valid_moves = []
            piece.candidate_moves = [i for i in self.get_adjacent_cells(piece.row, piece.col) 
                                     if self.in_boundaries(i.row, i.col)]
            for cell in piece.candidate_moves:
                adjacent_piece = self.find_piece(cell.row, cell.col)
                if adjacent_piece and not adjacent_piece.is_player:
                    # Project 1 cell
                    end = (2 * cell.row - piece.row, 2 * cell.col - piece.col)
                    if (
                            self.in_boundaries(end[0], end[1]) and
                            self.find_piece(end[0], end[1]) is None
                        ):
                        landing_square = Cell(end[0], end[1], adjacent_piece)
                        piece.capture_moves.append(landing_square)
                elif adjacent_piece is None:
                    valid_moves.append(cell)
            piece.candidate_moves = valid_moves


    def find_cell(self, row, col):
        if not self.selected_piece:
            return
        if self.selected_piece.candidate_moves:
            for i in self.selected_piece.candidate_moves:
                if i.row == row and i.col == col:
                    return i
        if self.selected_piece.double_captures:
            for i in self.selected_piece.double_captures:
                if i.row == row and i.col == col:
                    return i
        if self.selected_piece.capture_moves:
            for i in self.selected_piece.capture_moves:
                if i.row == row and i.col == col:
                    return i


    def check_double_captures(self):
        if not self.selected_piece:
            return
        piece = self.selected_piece
        if piece.capture_moves:
            #  LANDING SQUARE FROM THE FIRST CAPTURE BRANCHES INTO 2 SQUARES
            #  POTENTIALLY CONTAINING OPPONENT PIECES
            new_captures = []
            for square in piece.capture_moves:
                new_captures += [i for i in self.get_adjacent_cells(square.row, square.col)
                                if self.in_boundaries(i.row, i.col)]
            for square in new_captures:
                adjacent_piece = self.find_piece(square.row, square.col)
                if adjacent_piece and not adjacent_piece.is_player:
                    # Project 1 cell
                    end = (2 * square.row - square.origin_square.row, 2 * square.col - square.origin_square.col)
                    if (
                            self.in_boundaries(end[0], end[1]) and
                            self.find_piece(end[0], end[1]) is None
                        ):

                        first_capture_row = (piece.row + square.origin_square.row) // 2
                        first_capture_col = (piece.col + square.origin_square.col) // 2

                        result = self.find_piece(first_capture_row, first_capture_col)

                        landing_square = Cell(end[0], end[1], result, adjacent_piece, square.origin_square)
                        piece.double_captures.append(landing_square)


    def get_adjacent_cells(self, row, col):
        y_dir = 1 if self.player_turn else -1  # Invert y if we're a computer piece
        cell1 = (row - y_dir, col - 1)
        cell2 = (row - y_dir, col + 1)
        origin_square = Cell(row, col)
        left_cell = Cell(cell1[0], cell1[1], None, None, origin_square)
        right_cell = Cell(cell2[0], cell2[1], None, None, origin_square)
        if not self.selected_piece.is_king:
            return left_cell, right_cell
        else:
            cell3 = (row + y_dir, col - 1)
            cell4 = (row + y_dir, col + 1)
            back_left_cell = Cell(cell3[0], cell3[1],  None, None, origin_square)
            back_right_cell = Cell(cell4[0], cell4[1],  None, None, origin_square)
            return left_cell, right_cell, back_left_cell, back_right_cell


    def handle_mouseup(self, event):
        if self.selected_piece:
            piece = self.selected_piece
            if piece:
                piece.hidden = False  # Make piece visible again

            mouse_x, mouse_y = event.pos

            target_col = mouse_x // CELL_WIDTH
            target_row = (mouse_y - 50) // CELL_HEIGHT
            cell = self.find_cell(target_row, target_col)
            if not cell:
                self.selected_piece = None
                return

            # INITIATE REGULAR MOVE
            if cell in piece.candidate_moves:
                # Update attributes for piece object
                piece.row = target_row
                piece.col = target_col

                # King if end of board
                if target_row == 0:
                    piece.is_king = True

                self.selected_piece = None
                self.player_turn = False

            # INITIATE CAPTURE MOVE
            elif cell in piece.capture_moves or piece.double_captures:

                # Update attributes to move the piece object
                piece.row = target_row
                piece.col = target_col

                # King if end of board
                if target_row == 0:
                    piece.is_king = True

                # Remove enemy piece
                cell = self.find_cell(target_row, target_col)
                if not cell:
                    print('Error removing capture piece')
                elif cell in piece.capture_moves:
                    self.pieces.remove(cell.capture_piece)
                    print('Removed single capture piece')
                    self.player_score += 1
                elif cell in piece.double_captures:
                    self.pieces.remove(cell.capture_piece)
                    self.pieces.remove(cell.double_capture_piece)
                    print('Removed double capture pieces')
                    self.player_score += 2

                self.selected_piece = None

                self.player_turn = False

        self.selected_piece = None


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

    def ai_move(self):
        self.ai_regular_moves.clear()
        self.ai_capture_moves.clear()
        for row in range(8):
            for col in range(8):
                piece = self.find_piece(row, col)
                if piece and not piece.is_player:
                    potential_moves = [i for i in self.get_adjacent_cells(piece.row, piece.col)
                                       if self.in_boundaries(i.row, i.col)]
                    for target_row, target_col in potential_moves:
                        enemy_piece = self.find_piece(target_row, target_col)
                        if enemy_piece and enemy_piece.is_player:
                            landing_row = target_row + (target_row - row)
                            landing_col = target_col + (target_col - col)
                            if (
                                    self.in_boundaries(landing_row, landing_col)
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

