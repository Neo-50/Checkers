import pygame
# from random import choice

from constants import *
from cell import Cell
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
            Piece(self.window, 3, 3, False, False),
            Piece(self.window, 3, 5, False, False),
            Piece(self.window, 1, 1, False, False),
            Piece(self.window, 1, 3, False, False),
            Piece(self.window, 1, 5, False, False),
            Piece(self.window, 1, 7, False, False),

            # Piece(self.window, 5, 3, False, False),
            Piece(self.window, 5, 5, False, False),
            Piece(self.window, 7, 1, False, False),
            Piece(self.window, 7, 3, False, False),
            Piece(self.window, 7, 5, False, False),
            Piece(self.window, 7, 7, False, False),
            # Player
            Piece(self.window, 4, 4, True, False),
        ]

        self.selected_piece = None
        self.player_turn = True
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.player_score = 0


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

            elif adjacent_piece and adjacent_piece.is_player:
                print('Player piece in adjacent cell')
            elif adjacent_piece is None:
                valid_moves.append(cell)
            else:
                print('An error occurred!')
        piece.candidate_moves = valid_moves


    def check_double_captures(self):
        if not self.selected_piece:
            return
        piece = self.selected_piece
        if piece.capture_moves:
            #  LANDING SQUARE FROM THE FIRST CAPTURE BRANCHES INTO 2 SQUARES
            #  POTENTIALLY CONTAINING OPPONENT PIECES
            new_captures = []
            first_pieces = []
            for square in piece.capture_moves:
                first_pieces.append((square.capture_piece.row, square.capture_piece.col))
                new_captures += [i for i in self.get_adjacent_cells(square.row, square.col)
                                if self.in_boundaries(i.row, i.col)]
            for square in new_captures:
                # print(f'Cell attributes: ({vars(square)})')
                adjacent_piece = self.find_piece(square.row, square.col)
                if adjacent_piece and not adjacent_piece.is_player:
                    # Project 1 cell
                    end = (2 * square.row - square.origin_square.row, 2 * square.col - square.origin_square.col)
                    if (
                            self.in_boundaries(end[0], end[1]) and
                            self.find_piece(end[0], end[1]) is None
                        ):
                        capture1 = None
                        for j in first_pieces:
                            if adjacent_piece.row - 3 == piece.row:
                                if j[1] == adjacent_piece.col and j[0] - 1 == piece.row:
                                    capture1 = self.find_piece(j[0], j[1])
                                    break
                                elif j[1] + 2 == adjacent_piece.col and j[0] - 1 == piece.row:
                                    capture1 = self.find_piece(j[0], j[1])
                                    break
                                elif j[1] - 2 == adjacent_piece.col and j[0] - 1 == piece.row:
                                    capture1 = self.find_piece(j[0], j[1])
                                    break
                            elif adjacent_piece.row + 3 == piece.row:
                                if j[1] == adjacent_piece.col and j[0] + 1 == piece.row:
                                    capture1 = self.find_piece(j[0], j[1])
                                    break
                                elif j[1] + 2 == adjacent_piece.col and j[0] + 1 == piece.row:
                                    capture1 = self.find_piece(j[0], j[1])
                                    break
                                elif j[1] - 2 == adjacent_piece.col and j[0] + 1 == piece.row:
                                    capture1 = self.find_piece(j[0], j[1])
                                    break
                        landing_square = Cell(end[0], end[1], capture1, adjacent_piece, square.origin_square)
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

                print('Player moved to ', target_row, target_col)

                # King if end of board
                if target_row == 0:
                    piece.is_king = True

                self.selected_piece = None
                # self.player_turn = False

            # INITIATE DOUBLE CAPTURE MOVE
            if cell in piece.double_captures:
                print('Double capture move initiated!')

                # Update attributes to move the piece object
                piece.row = target_row
                piece.col = target_col

                if target_row == 0:
                    piece.is_king = True

                self.pieces.remove(cell.capture_piece)
                self.pieces.remove(cell.double_capture_piece)

                self.selected_piece = None
                # self.player_turn = False

            # INITIATE CAPTURE MOVE
            elif cell in piece.capture_moves:

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
                else:
                    self.pieces.remove(cell.capture_piece)

                self.selected_piece = None
                # self.player_turn = False

        self.selected_piece = None


    def find_piece(self, target_row, target_col):
        for piece in self.pieces:
            if piece.row == target_row and piece.col == target_col:
                return piece
        return None


    def find_cell(self, row, col):
        if not self.selected_piece:
            return
        if self.selected_piece.candidate_moves:
            for i in self.selected_piece.candidate_moves:
                if i.row == row and i.col == col:
                    print('Found regular square')
                    return i
        if self.selected_piece.double_captures:
            for i in self.selected_piece.double_captures:
                if i.row == row and i.col == col:
                    print('Found double capture square')
                    return i
        if self.selected_piece.capture_moves:
            for i in self.selected_piece.capture_moves:
                if i.row == row and i.col == col:
                    print('Found regular capture square')
                    return i


    def draw(self):
        self.window.fill((200, 200, 200))
        self.draw_grid()
        self.draw_scoreboard()
        # Draw all pieces except the animating one
        for piece in self.pieces:
            if not piece.hidden:
                piece.draw()
        self.draw_dragging_piece()


    def draw_grid(self):
        light_color = (240, 217, 181)  # Light tan
        dark_color = (181, 136, 99)  # Darker brown

        margin_color = (150, 180, 220)

        margin_rect = pygame.Rect(0, 0, BOARD_WIDTH, SCOREBOARD_HEIGHT)
        pygame.draw.rect(self.window, margin_color, margin_rect)

        for row in range(9):
            for col in range(9):
                rect = pygame.Rect(col * CELL_WIDTH, (row * CELL_HEIGHT) + 50, CELL_WIDTH, CELL_HEIGHT)
                if (row + col) % 2 == 0:
                    color = light_color
                else:
                    color = dark_color
                pygame.draw.rect(self.window, color, rect)
        self.draw_highlighted_cells()


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

        score_text = font.render(f'Player: {self.player_score}', True, text_color)
        title_text = font.render('Checkers', True, text_color)

        score_text_width = score_text.get_width()

        score_text_x = self.window.get_width() - score_text_width - 10
        score_text_y = 10

        self.window.blit(score_text, (score_text_x, score_text_y))
        self.window.blit(title_text, (10, score_text_y))
