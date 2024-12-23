import pygame
from random import choice

from constants import *
from piece import Piece
from cell import Cell
from vector import Vector
from move import Move
from board_grid import BoardGrid
from scoreboard import Scoreboard

PIECE_POSITIONS = {
    'computer': [
        Cell(0, 0), Cell(0, 2), Cell(0, 4), Cell(0, 6),
        Cell(1, 1), Cell(1, 3), Cell(1, 5), Cell(1, 7),
        Cell(2, 0), Cell(2, 2), Cell(2, 4), Cell(2, 6)
    ],
    'player': [
        Cell(5, 1), Cell(5, 3), Cell(5, 5), Cell(5, 7),
        Cell(6, 0), Cell(6, 2), Cell(6, 4), Cell(6, 6),
        Cell(7, 1), Cell(7, 3), Cell(7, 5), Cell(7, 7)
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
        self.candidate_moves = []

    def init_pieces(self):
        self.pieces = []
        for cell in PIECE_POSITIONS['player']:
            self.pieces.append(self.make_piece(cell, True))
        for cell in PIECE_POSITIONS['computer']:
            self.pieces.append(self.make_piece(cell, False))

    def make_piece(self, cell, is_player):
        return Piece(self.window, cell, is_player, self.handle_piece_mousedown)

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
        if event.type == pygame.MOUSEBUTTONUP:
            self.selected_piece = None

    def draw_pieces(self):
        for piece in self.pieces:
            piece.draw()

    def find_piece(self, cell):
        for piece in self.pieces:
            if piece.position == cell:
                return piece
        return None

    @staticmethod
    def cell_is_in_board(cell):
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
        self.find_candidate_moves(piece)

    def handle_grid_mouseup(self, cell):
        if not self.player_turn:
            return
        if self.selected_piece:
            self.selected_piece.show()

            move = next((obj for obj in self.candidate_moves if obj.end == cell), None)
            if not move:
                return

            move.piece.set_position(move.end)

            if move.is_capture():
                print(f'Removing capture piece at: ({move.captures_piece.position.row}, {move.captures_piece.position.col})')
                self.pieces.remove(move.captures_piece)
                self.scoreboard.increment_player_score()

        self.candidate_moves = []
        self.selected_piece = None
        self.player_turn = False

    def find_candidate_moves(self, piece):
        for adjacent in piece.get_adjacent_cells():
            if self.cell_is_in_board(adjacent):
                adjacent_piece = self.find_piece(adjacent)
                if adjacent_piece:
                    if not adjacent_piece.is_player:
                        end = Cell(2 * adjacent.row - piece.position.row,
                                   2 * adjacent.col - piece.position.col)  # Project 1 more cell
                        if (
                                self.cell_is_in_board(end) and
                                self.find_piece(end) is None
                        ):
                            self.candidate_moves.append(Move(piece, end, adjacent_piece))
                            self.grid.highlight_cell(end)
                else:
                    self.candidate_moves.append(Move(piece, adjacent))
                    self.grid.highlight_cell(adjacent)

    def ai_move(self):
        capture_moves = []
        regular_moves = []

        for piece in self.pieces:
            if piece.is_player:
                continue
            for adjacent in piece.get_adjacent_cells():
                if self.cell_is_in_board(adjacent):
                    adjacent_piece = self.find_piece(adjacent)
                    if adjacent_piece:
                        if adjacent_piece.is_player:
                            end = Cell(2 * adjacent.row - piece.position.row,
                                       2 * adjacent.col - piece.position.col)  # Project 1 more cell
                            if (
                                    self.cell_is_in_board(end) and
                                    not self.find_piece(end)
                            ):
                                capture_moves.append(Move(piece, end, adjacent_piece))
                    else:
                        regular_moves.append(Move(piece, adjacent))
        if len(capture_moves) > 0:
            move = choice(capture_moves)
            self.pieces.remove(move.captures_piece)
            move.piece.set_position(move.end)
            if move.end.col == NUM_ROWS - 1:
                move.piece.promote()
            self.scoreboard.increment_computer_score()
        elif len(regular_moves) > 0:
            move = choice(regular_moves)
            move.piece.set_position(move.end)
            if move.end.col == NUM_COLS - 1:
                move.piece.promote()
        else:
            print("No valid moves for AI!")
