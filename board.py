import pygame
from random import choice

from constants import *
from piece import Piece
from vector import Vector
from board_grid import BoardGrid
from scoreboard import Scoreboard

PIECE_POSITIONS = {
    'computer': [
        (0,0), (0,2), (0,4), (0,6),
        (1,1), (1,3), (1,5), (1,7),
        (2,0), (2,2), (2,4), (2,6)
    ],
    'player': [
        (5,1), (5,3), (5,5), (5,7),
        (6,0), (6,2), (6,4), (6,6),
        (7,1), (7,3), (7,5), (7,7)
    ]
}

class Board:
    def __init__(self, window):
        self.window = window
        self.scoreboard = Scoreboard(self.window)
        self.grid = BoardGrid(self.window, Vector(0, SCOREBOARD_HEIGHT), self.handle_grid_mouseup)
        self.init_pieces()

        self.selected_piece = None
        self.player_turn = True
        self.drag_offset = Vector(0, 0)

        self.regular_moves = []
        self.capture_moves = []
        self.capture_pieces = []

    def init_pieces(self):
        self.pieces = []
        for pos in PIECE_POSITIONS['player']:
            self.pieces.append(self.make_piece(pos[0], pos[1], True))
        for pos in PIECE_POSITIONS['computer']:
            self.pieces.append(self.make_piece(pos[0], pos[1], False))

    def make_piece(self, row, col, is_player):
        return Piece(self.window, row, col, is_player, self.handle_piece_mousedown)

    def update(self):
        if (not self.player_turn):
            self.ai_move()
            self.player_turn = True

    def draw(self):
        self.clear()
        self.scoreboard.draw()
        self.grid.draw()
        self.draw_pieces()
        self.draw_selected_piece()

    def clear(self):
        self.window.fill((200, 200, 200))

    def handle_event(self, event):
        self.grid.handle_event(event)
        for piece in self.pieces:
            piece.handle_event(event)

    def draw_pieces(self):
        for piece in self.pieces:
            piece.draw()

    def find_piece(self, row, col):
        for piece in self.pieces:
            if piece.row == row and piece.col == col:
                return piece
        return None

    def find_possible_player_moves(self, piece):
        if piece.is_king:
            return [
                (piece.row - 1, piece.col - 1),  # Top left
                (piece.row - 1, piece.col + 1),  # Top right
                (piece.row + 1, piece.col - 1),  # Bottom left
                (piece.row + 1, piece.col + 1)   # Bottom right
            ]
        else:
            return [
                (piece.row - 1, piece.col - 1),  # Top left
                (piece.row - 1, piece.col + 1)   # Top right
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
        self.selected_piece.hide()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_position = Vector(mouse_x, mouse_y)
        piece_position = mouse_position - self.drag_offset
        pygame.draw.circle(self.window, self.selected_piece.get_color(), piece_position.tuple(), PIECE_RADIUS)

    def handle_piece_mousedown(self, piece, event):
        if not self.player_turn:
            return
        self.selected_piece = piece
        mouse_position = Vector(event.pos[0], event.pos[1])
        piece_position = piece.get_absolute_position()
        self.drag_offset = mouse_position - piece_position
        self.do_player_move(piece)

    def handle_grid_mouseup(self, cell):
        if not self.player_turn:
            return
        if self.selected_piece:
            self.selected_piece.show()

            # INITIATE REGULAR MOVE
            if (cell.row, cell.col) in self.regular_moves:

                # Update attributes for piece object
                self.selected_piece.row = cell.row
                self.selected_piece.col = cell.col

                print('Player moved to ', cell.row, cell.col)

                # King if end of board
                if cell.row == 0:
                    self.selected_piece.is_king = True

                self.player_turn = False

            # INITIATE CAPTURE MOVE
            elif (cell.row, cell.col) in self.capture_moves:

                # Update attributes to move the piece object
                self.selected_piece.row = cell.row
                self.selected_piece.col = cell.col

                # King if end of board
                if cell.row == 0:
                    self.selected_piece.is_king = True

                # Remove enemy piece
                if self.capture_moves and self.capture_pieces:  # Ensure lists are not empty
                    captured = False
                    for i, move in enumerate(self.capture_moves):
                        if (cell.row, cell.col) == move:
                            enemy_piece = self.find_piece(self.capture_pieces[i][0], self.capture_pieces[i][1])
                            if enemy_piece:
                                self.pieces.remove(enemy_piece)
                                print(f'Piece removed: ({enemy_piece.row}, {enemy_piece.col})')
                                captured = True
                                break
                    if not captured:
                        print("Error: Target square does not match any capture moves.")
                else:
                    print('Error: Capture moves or capture pieces are empty')

                self.scoreboard.increment_player_score()
                self.player_turn = False

            else:
                print('Error: Moves list is empty or target square does not match moves list')

        self.regular_moves.clear()
        self.capture_moves.clear()
        self.capture_pieces.clear()
        self.selected_piece = None

    def ai_move(self):
        for row in range(NUM_ROWS):
            for col in range(NUM_COLS):
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

            self.scoreboard.increment_computer_score()

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
