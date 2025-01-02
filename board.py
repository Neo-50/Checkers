import pygame
from constants import *
from piece import Piece
from move import Move
from random import choice

'''
Responsibilies:
    1. Draw the game grid and pieces on the screen (shapes, colors)
    2. Hold the board data (array)
    3. Make moves
'''

PIECE_POSITIONS = {
    'computer': [
        (0, 0), (0, 2), (0, 4), (0, 6),
        (1, 1), (1, 3), (1, 5), (1, 7),
        (2, 0), (2, 2), (2, 4), (2, 6)
    ],
    'player': [
        (5, 1), (5, 3), (5, 5), (5, 7),
        (6, 0), (6, 2), (6, 4), (6, 6),
        (7, 1), (7, 3), (7, 5), (7, 7)
    ]
}

class Board:
    def __init__(self, window):
        self.window = window
        self.pieces = []
        self.init_pieces()
        self.selected_piece = None
        self.ai_piece = None
        self.player_turn = True
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.player_score = 0
        self.ai_score = 0
        self.turn_count = 1
        self.wait_a_bit = False

        self.ai_regular_moves = []
        self.ai_capture_moves = []
        self.next_capture = None

        self.delay_start_time = None
        self.waiting_to_remove = False
        self.pending_capture = None
        self.capture_display = ''
        self.capture_display_start_time = 0

        # Animation state variables
        self.animating_piece = None
        self.animation_start = None
        self.animation_end = None
        self.animation_progress = 0  # Progress percentage (0 to 1)
        self.animation_speed = 0.05  # Adjust for animation speed

    def init_pieces(self):
        self.pieces = []
        for square in PIECE_POSITIONS['player']:
            self.pieces.append(self.make_piece(square[0], square[1], True))
        for square in PIECE_POSITIONS['computer']:
            self.pieces.append(self.make_piece(square[0], square[1], False))

    def make_piece(self, row, col, is_player):
        return Piece(self.window, row, col, is_player, False)

    def update(self):
        if self.wait_a_bit:
            pygame.time.wait(500)
            self.wait_a_bit = False
        if self.animating_piece:
            # Process animation progress
            self.animation_progress += self.animation_speed
            if self.animation_progress >= 1:
                self.animation_progress = 1  # Clamp progress
                self.animating_piece.row, self.animating_piece.col = self.animation_end
                self.animating_piece = None  # End animation

                # Handle capture
                if self.pending_capture:
                    self.pieces.remove(self.pending_capture)
                    self.pending_capture = None
                    self.waiting_to_remove = False

                    self.wait_a_bit = True
                    # Setup second capture variables for draw
                    if self.next_capture:
                        self.animation_start = self.next_capture["start"]
                        self.animation_end = self.next_capture["end"]
                        self.pending_capture = self.next_capture["capture_piece"]
                        self.animating_piece = self.ai_piece
                        self.animation_progress = 0  # Reset animation
                        self.next_capture = None
                    else:
                        # End AI turn
                        if self.animation_end[0] == 7:  # King if at the end
                            self.ai_piece.is_king = True
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

        if self.selected_piece:
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

        if self.capture_display:
            current_time = pygame.time.get_ticks()
            if self.capture_display_start_time + 3000 <= current_time:
                self.capture_display = ''
                self.capture_display_start_time = 0

        score_text = font.render(f'Player: {self.player_score}    |    AI: {self.ai_score}', True, text_color)
        title_text = font.render(f'Checkers         Turn: {self.turn_count}        {self.capture_display}',True, text_color)

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

    def find_ai_piece(self, target_row, target_col):
        for piece in self.pieces:
            if piece.row == target_row and piece.col == target_col and not piece.is_player:
                return piece
        return None

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
                        landing_square = Move(end[0], end[1], adjacent_piece)
                        piece.capture_moves.append(landing_square)
                elif adjacent_piece is None:
                    valid_moves.append(cell)
            piece.candidate_moves = valid_moves

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

                        landing_square = Move(end[0], end[1], result, adjacent_piece, square.origin_square)
                        piece.double_captures.append(landing_square)

    def get_adjacent_cells(self, row, col):
        y_dir = 1 if self.player_turn else -1  # Invert y if we're a computer piece
        cell1 = (row - y_dir, col - 1)
        cell2 = (row - y_dir, col + 1)
        origin_square = Move(row, col)
        left_cell = Move(cell1[0], cell1[1], None, None, origin_square)
        right_cell = Move(cell2[0], cell2[1], None, None, origin_square)
        if self.player_turn and not self.selected_piece.is_king:
            return left_cell, right_cell
        elif not self.player_turn and not self.ai_piece.is_king:
            return left_cell, right_cell
        else:
            cell3 = (row + y_dir, col - 1)
            cell4 = (row + y_dir, col + 1)
            back_left_cell = Move(cell3[0], cell3[1], None, None, origin_square)
            back_right_cell = Move(cell4[0], cell4[1], None, None, origin_square)
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
                if piece.double_captures:
                    self.capture_display = 'Double capture move!'
                    self.capture_display_start_time = pygame.time.get_ticks()
                elif piece.capture_moves:
                    self.capture_display = 'Capture move!'
                    self.capture_display_start_time = pygame.time.get_ticks()
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
                    self.player_score += 1
                elif cell in piece.double_captures:
                    self.pieces.remove(cell.capture_piece)
                    self.pieces.remove(cell.double_capture_piece)
                    self.player_score += 2

                self.selected_piece = None
                self.player_turn = False

        self.selected_piece = None
        self.ai_move()

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

    # noinspection PyUnboundLocalVariable
    def ai_move(self):
        if self.player_turn:
            return

        self.ai_piece = None

        ai_pieces = []
        ai_attack_pieces = []
        ai_regular_pieces = []

        for row in range(8):
            for col in range(8):
                check_piece = self.find_ai_piece(row, col)
                if check_piece:
                    ai_pieces.append(check_piece)
        for p in ai_pieces:
            self.ai_piece = p
            self.ai_piece.regular_moves.clear()
            self.ai_piece.capture_moves.clear()
            self.ai_piece.double_captures.clear()
            p.regular_moves = [i for i in self.get_adjacent_cells(self.ai_piece.row, self.ai_piece.col)
                               if self.in_boundaries(i.row, i.col)
                               and not self.find_piece(i.row, i.col)]
            p.candidate_moves = [i for i in self.get_adjacent_cells(self.ai_piece.row, self.ai_piece.col)
                                 if self.in_boundaries(i.row, i.col)
                                 and (piece := self.find_piece(i.row, i.col)) is not None
                                 and piece.is_player]
            for s in p.candidate_moves:
                landing_row = s.row + (s.row - s.origin_square.row)
                landing_col = s.col + (s.col - s.origin_square.col)
                enemy_piece = self.find_piece(s.row, s.col)
                if (
                        self.in_boundaries(landing_row, landing_col)
                        and not self.find_piece(landing_row, landing_col)
                ):
                    capture_move = Move(landing_row, landing_col, enemy_piece,
                                        None, s.origin_square)
                    self.ai_piece.capture_moves.append(capture_move)
        for a in ai_pieces:
            if a.capture_moves:
                ai_attack_pieces.append(a)
            elif a.regular_moves:
                ai_regular_pieces.append(a)
        if ai_attack_pieces:
            for ap in ai_attack_pieces:
                for cm in ap.capture_moves:
                    ai_capture_branch_2 = [i for i in self.get_adjacent_cells(cm.row, cm.col)
                                           if self.in_boundaries(i.row, i.col)
                                           and (piece := self.find_piece(i.row, i.col)) is not None
                                           and piece.is_player]
                    if ai_capture_branch_2:
                        for square2 in ai_capture_branch_2:
                            landing_row2 = square2.row + (square2.row - square2.origin_square.row)
                            landing_col2 = square2.col + (square2.col - square2.origin_square.col)
                            enemy_piece = self.find_piece(square2.row, square2.col)
                            if (
                                    self.in_boundaries(landing_row2, landing_col2)
                                    and not self.find_piece(landing_row2, landing_col2)
                            ):
                                first_capture_row = (ap.row + square2.origin_square.row) // 2
                                first_capture_col = (ap.col + square2.origin_square.col) // 2

                                result = self.find_piece(first_capture_row, first_capture_col)

                                double_attack_move = Move(landing_row2, landing_col2, result,
                                                          enemy_piece, square2.origin_square)

                                ap.double_captures.append(double_attack_move)
            for ap in ai_attack_pieces:
                if ap.double_captures:
                    self.ai_piece = ap

                    double_move_choice = choice(self.ai_piece.double_captures)

                    # Set up animation for the first capture
                    self.animating_piece = self.ai_piece
                    self.animation_start = [ap.row, ap.col]
                    self.animation_end = [double_move_choice.origin_square.row,
                                          double_move_choice.origin_square.col]
                    self.animation_progress = 0  # Reset progress
                    self.delay_start_time = pygame.time.get_ticks()
                    self.pending_capture = double_move_choice.capture_piece
                    self.waiting_to_remove = True

                    # Save the second capture details for later
                    self.next_capture = {
                        "start": [double_move_choice.origin_square.row, double_move_choice.origin_square.col],
                        "end": [double_move_choice.row, double_move_choice.col],
                        "capture_piece": double_move_choice.double_capture_piece
                    }
                    # King if end of board
                    if double_move_choice.row == 7:
                        self.ai_piece.is_king = True
                        self.capture_display = 'Double capture move with King promotion!'
                        self.capture_display_start_time = pygame.time.get_ticks()
                    else:
                        self.capture_display = 'Double capture move!'
                        self.capture_display_start_time = pygame.time.get_ticks()
                    self.ai_score += 2
                    self.turn_count += 1
                    self.player_turn = True

                elif ap.capture_moves and not ap.double_captures:
                    self.ai_piece = choice(ai_attack_pieces)

                    capture_move_choice = choice(self.ai_piece.capture_moves)

                    # Set up animation
                    self.animating_piece = self.ai_piece
                    self.animation_start = [capture_move_choice.origin_square.row,
                                            capture_move_choice.origin_square.col]
                    self.animation_end = [capture_move_choice.row, capture_move_choice.col]
                    self.animation_progress = 0  # Reset progress

                    self.pending_capture = capture_move_choice.capture_piece
                    self.waiting_to_remove = True

                    # King if end of board
                    if capture_move_choice.row == 7:
                        self.ai_piece.is_king = True
                        self.capture_display = 'Capture move with King promotion!'
                        self.capture_display_start_time = pygame.time.get_ticks()
                    else:
                        self.capture_display = 'Capture move!'
                        self.capture_display_start_time = pygame.time.get_ticks()
                    self.ai_score += 1
                    self.turn_count += 1
                    self.player_turn = True

        elif ai_regular_pieces:
            for x in ai_regular_pieces:
                for move3 in x.regular_moves:
                    x.safe_moves.clear()
                    check_enemies = [i for i in self.get_adjacent_cells(move3.row, move3.col)
                               if self.in_boundaries(i.row, i.col)
                               and (piece8 := self.find_piece(i.row, i.col)) is not None
                               and piece8.is_player]
                    if not check_enemies:
                        x.safe_moves.append(move3)
            safe_pieces = []

            for z in ai_regular_pieces:
                if z.safe_moves:
                    safe_pieces.append(z)

            for z in ai_regular_pieces:
                if z.safe_moves:
                    safe_pieces.append(z)

            if safe_pieces:
                # Filter for kings and pieces with the highest row number in safe_pieces
                print('Safe piece found!')
                max_row = max(p.row for p in safe_pieces)
                prioritized_pieces = [p for p in safe_pieces if p.is_king or p.row == max_row]
                for pp in prioritized_pieces:
                    print('Priority safe pieces: ', pp.row, pp.col)
            else:
                # If no safe pieces, fallback to regular pieces
                print('No safe pieces found :(')
                max_row = max(p.row for p in ai_regular_pieces)
                prioritized_pieces = [p for p in ai_regular_pieces if p.row == max_row]
                for pp in prioritized_pieces:
                    print('Priority non-safe pieces: ', pp.row, pp.col)

            # Choose a piece from the prioritized list
            self.ai_piece = choice(prioritized_pieces)
            print(f'Chosen piece at: {self.ai_piece.row}, {self.ai_piece.col}')

            # Prioritize moves for the chosen piece
            moves = self.ai_piece.safe_moves if safe_pieces else self.ai_piece.regular_moves
            max_target_row = max(m.row for m in moves)
            prioritized_moves = [m for m in moves if m.row == max_target_row]

            # Choose a move from the prioritized moves
            regular_move_choice = choice(prioritized_moves)
            print(f'Chosen move to: {regular_move_choice.row}, {regular_move_choice.col}')

            # Set up animation
            self.animating_piece = self.ai_piece
            self.animation_start = [regular_move_choice.origin_square.row, regular_move_choice.origin_square.col]
            self.animation_end = [regular_move_choice.row, regular_move_choice.col]
            self.animation_progress = 0  # Reset progress

            # Set up animation (regular_move_choice is guaranteed to be defined here)
            self.animating_piece = self.ai_piece
            self.animation_start = [regular_move_choice.origin_square.row, regular_move_choice.origin_square.col]
            self.animation_end = [regular_move_choice.row, regular_move_choice.col]
            self.animation_progress = 0  # Reset progress

            self.animating_piece = self.ai_piece
            self.animation_start = [regular_move_choice.origin_square.row, regular_move_choice.origin_square.col]
            self.animation_end = [regular_move_choice.row, regular_move_choice.col]
            self.animation_progress = 0  # Reset progress

            # King if end of board
            if regular_move_choice.row == 7:
                self.ai_piece.is_king = True

            self.turn_count += 1
            self.player_turn = True
        else:
            print('No valid moves for AI!')