import pygame
from random import choice

from constants import *
from piece import Piece
from cell import Cell
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
        if not self.player_turn:
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

    def find_piece(self, cell):
        for piece in self.pieces:
            if piece.row == cell.row and piece.col == cell.col:
                return piece
        return None

    def cell_is_in_board(self, cell):
        return 0 <= cell.row < NUM_ROWS and 0 <= cell.col < NUM_COLS

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
        self.find_player_moves(piece)

    def handle_grid_mouseup(self, cell):
        if not self.player_turn:
            return
        if self.selected_piece:
            self.selected_piece.show()

            # INITIATE REGULAR MOVE
            if (cell.row, cell.col) in self.regular_moves:
                self.selected_piece.row = cell.row
                self.selected_piece.col = cell.col]]
                if cell.row == 0:
                    self.selected_piece.promote()
                self.player_turn = False

            # INITIATE CAPTURE MOVE
            elif (cell.row, cell.col) in self.capture_moves:
                self.selected_piece.row = cell.row
                self.selected_piece.col = cell.col
                if cell.row == 0:
                    self.selected_piece.promote()
                if self.capture_moves and self.capture_pieces:  # Ensure lists are not empty
                    for i, move in enumerate(self.capture_moves):
                        if (cell.row, cell.col) == move:
                            enemy_piece = self.capture_pieces[i]
                            if enemy_piece:
                                self.pieces.remove(enemy_piece)
                                print(f'Piece removed: ({enemy_piece.row}, {enemy_piece.col})')
                                break
                self.scoreboard.increment_player_score()
                self.player_turn = False

        self.regular_moves.clear()
        self.capture_moves.clear()
        self.capture_pieces.clear()
        self.selected_piece = None

    def find_player_moves(self, piece):
        self.regular_moves.clear()
        self.capture_moves.clear()
        self.capture_pieces.clear()
        
        for adjacent in piece.get_adjacent_cells():
            if self.cell_is_in_board(adjacent):
                adjacent_piece = self.find_piece(adjacent)
                if not adjacent_piece:
                    self.regular_moves.append((adjacent.row, adjacent.col))
                elif not adjacent_piece.is_player:
                    self.capture_pieces.append(adjacent_piece)
                    landing_cell = Cell(2 * adjacent.row - piece.row, 2 * adjacent.col - piece.col) # Project 1 more cell
                    if (
                        self.cell_is_in_board(landing_cell) and
                        self.find_piece(landing_cell) is None
                    ):
                        self.capture_moves.append((landing_cell.row, landing_cell.col))

    def ai_move(self):
        for row in range(NUM_ROWS):
            for col in range(NUM_COLS):
                piece = self.find_piece(Cell(row, col))
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
                            enemy_piece = self.find_piece(Cell(target_row, target_col))
                            if enemy_piece and enemy_piece.is_player:
                                # Calculate the landing square
                                landing_row = target_row + (target_row - row)
                                landing_col = target_col + (target_col - col)
                                if (
                                        0 <= landing_row < 8 and 0 <= landing_col < 8
                                        and not self.find_piece(Cell(landing_row, landing_col))
                                ):
                                    self.capture_moves.append(
                                        ((row, col), (landing_row, landing_col), (target_row, target_col)))

                            # Check for regular moves
                            elif not self.find_piece(Cell(target_row, target_col)):
                                self.regular_moves.append(((row, col), (target_row, target_col)))

        if self.capture_moves:
            # Execute a capture (prioritized over regular moves)
            start, end, captured = choice(self.capture_moves)

            ai_piece = self.find_piece(Cell(start[0], start[1]))

            capture_piece = self.find_piece(Cell(captured[0], captured[1]))
            self.pieces.remove(capture_piece)
            ai_piece.set_position(end[0], end[1])

            # King if end of board
            if end[0] == 7:
                ai_piece.promote()

            self.scoreboard.increment_computer_score()

        elif self.regular_moves:
            # Execute a regular move
            start, end = choice(self.regular_moves)

            ai_piece = self.find_piece(Cell(start[0], start[1]))
            ai_piece.set_position(end[0], end[1])

            # King if end of board
            if end[0] == NUM_COLS - 1:
                ai_piece.promote()

        else:
            print("No valid moves for AI!")
