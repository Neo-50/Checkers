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
        self.selected_piece_color = None
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
        self.capture_piece = None

    def update(self):
        if not self.player_turn:
            self.ai_move()
            self.player_turn = True

    def draw(self):
        self.clear()
        self.draw_grid()
        self.draw_pieces()
        self.draw_dragging_piece()
        pygame.time.wait(40)

    def clear(self):
        self.window.fill((200, 200, 200))

    def draw_grid(self):
        light_color = (240, 217, 181)  # Light tan
        dark_color = (181, 136, 99)  # Darker brown
        border_color = (0, 255, 0)  # Green border for valid moves
        capture_color = (255, 0, 0)

        for row in range(8):
            for col in range(8):
                rect = pygame.Rect(col * CELL_WIDTH, row * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT)
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

    def draw_pieces(self):
        for piece in self.pieces:
            if not piece.hidden:
                piece.draw()

    def find_piece(self, target_row, target_col):
        for piece in self.pieces:
            if piece.row == target_row and piece.col == target_col:
                return piece
        return None

    def handle_mousedown(self, event):
        mouse_x, mouse_y = event.pos
        row = mouse_y // CELL_HEIGHT
        col = mouse_x // CELL_WIDTH
        radius = (CELL_WIDTH // 2) - PADDING
        for piece in self.pieces:
            piece_x = piece.col * CELL_WIDTH + CELL_WIDTH // 2
            piece_y = piece.row * CELL_HEIGHT + CELL_HEIGHT // 2
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
            target_row = mouse_y // CELL_HEIGHT

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

                pygame.time.wait(200)

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
                    if (target_row, target_col) == self.capture_moves[0]:
                        print('1 enemy piece found at: ', self.capture_pieces[0])

                        enemy_piece = self.find_piece(self.capture_pieces[0][0], self.capture_pieces[0][1])
                        if enemy_piece:
                            self.pieces.remove(enemy_piece)
                            print('Removed enemy piece at ', self.capture_pieces[0][0],
                                  self.capture_pieces[0][1])
                            print('----------------------')

                    elif len(self.capture_moves) > 1 and len(self.capture_pieces) > 1 and (target_row, target_col) == self.capture_moves[1]:
                        print('2 enemy pieces found at: ', self.capture_pieces[0], self.capture_pieces[1])
                        print('----------------------')

                        enemy_piece = self.find_piece(self.capture_pieces[1][0], self.capture_pieces[1][1])
                        if enemy_piece:
                            self.pieces.remove(enemy_piece)
                            print('Removed enemy piece at ', self.capture_pieces[1][0],
                                  self.capture_pieces[1][1])
                    else:
                        # Handle unexpected target_row/target_col
                        print("Error: Target square does not match any capture moves.")

                pygame.time.wait(500)

                # Increase score, end turn
                self.player_score += 1

                self.player_turn = False
            else:
                print('Else activated')
                # print('Not a regular or a capture move!')
                # print('Regular moves: ', self.regular_moves)
                # print('Pieces to capture ', self.capture_pieces)

        self.regular_moves = []
        self.valid_moves = []
        self.capture_moves = []
        self.capture_piece = []
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
            ai_piece.row = end[0]
            ai_piece.col = end[1]

            capture_piece = self.find_piece(captured[0], captured[1])
            if capture_piece:
                self.pieces.remove(capture_piece)
            print(f"AI captures piece at {captured} by moving from {start} to {end}")

            self.ai_score += 1
            print('AI score is now: ', self.ai_score)
        elif self.regular_moves:
            # Execute a regular move
            start, end = choice(self.regular_moves)
            ai_piece = self.find_piece(start[0], start[1])
            ai_piece.row = end[0]
            ai_piece.col = end[1]
            print(f'AI moved from {start} to {end}')
        else:
            print("No valid moves for AI!")


'''
    def handle_mouseup(self, event):
        if self.selected_piece:
            mouse_x, mouse_y = event.pos

            target_col = mouse_x // CELL_WIDTH
            target_row = mouse_y // CELL_HEIGHT

            if (target_row, target_col) in self.regular_moves:
                # Clear old position
                self.data[self.selected_piece[0]][self.selected_piece[1]] = None
                # King if end of board
                if target_row == 0:
                    self.selected_piece_color = 'rking'
                # Set new position
                self.data[target_row][target_col] = self.selected_piece_color
                print(f'Player moved from {self.selected_piece[0]}, {self.selected_piece[1]} to '
                      f'{target_row}, {target_col}')
                print('Regular moves mouseup: ', self.regular_moves)
                print('Capture moves mouseup: ', self.capture_moves)
                self.player_turn = False  # Change turn flag

            if (target_row, target_col) in self.capture_moves:
                # Clear old position
                self.data[self.selected_piece[0]][self.selected_piece[1]] = None
                # King if end of board
                if target_row == 0:
                    self.selected_piece_color = 'rking'
                # Set new position
                self.data[target_row][target_col] = self.selected_piece_color
                pygame.time.wait(300)
                # Clear opponent piece
                self.data[self.capture_piece[0]][self.capture_piece[1]] = None

                # Increase score, end turn
                self.player_score += 1

                print(f'Player captured piece at {self.capture_piece}. \n'
                      f'Contents of cell at captured piece location: '
                      f'{self.data[self.capture_piece[0]][self.capture_piece[1]]} \n'
                      f'Player score is now: {self.player_score}')

                self.player_turn = False  # Change turn flag

        self.regular_moves = []
        self.valid_moves = []
        self.capture_moves = []
        self.selected_piece = None  # Reset dragging state
        
        
        
        def ai_move(self):
        capture_moves = []
        regular_moves = []

        for row in range(8):
            for col in range(8):
                if self.pieces[row][col] == 'black':  # Check for AI pieces
                    potential_moves = [
                        (row + 1, col - 1),  # Forward-left
                        (row + 1, col + 1),  # Forward-right
                    ]
                    for target_row, target_col in potential_moves:
                        if 0 <= target_row < 8 and 0 <= target_col < 8:  # Within boundaries
                            # Check if opponent's piece is in the target square
                            if self.data[target_row][target_col] in ['red', 'rking']:
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
        elif regular_moves:
            # Execute a regular move
            start, end = choice(regular_moves)
            print(f"AI moves from {start} to {end}")
            self.data[start[0]][start[1]] = None  # Remove AI piece from start
            self.data[end[0]][end[1]] = 'black'  # Place AI piece in target square
        else:
            print("No valid moves for AI!")


    def select_piece(self, mouse_x, mouse_y, row, col):
        piece_x = col * CELL_WIDTH + CELL_WIDTH // 2
        piece_y = row * CELL_HEIGHT + CELL_HEIGHT // 2
        radius = (CELL_WIDTH // 2) - PADDING

        # Check if the click is within the piece's circle
        if (mouse_x - piece_x) ** 2 + (mouse_y - piece_y) ** 2 <= radius ** 2:
            # Set dragging-related attributes
            self.selected_piece = (row, col)
            self.drag_offset_x = mouse_x - piece_x
            self.drag_offset_y = mouse_y - piece_y
            return row, col
        return False  # No piece was selected


    @staticmethod
    def find_piece(pieces, target_row, target_col):

        for piece in pieces:
            if piece.row == target_row and piece.col == target_col:
                return target_row, target_col
        return None

            
    def select_piece(self, event, row, col, piece_color):
        mouse_x, mouse_y = event.pos
        piece_x = col * self.board.cell_width + self.board.cell_width // 2
        piece_y = row * self.board.cell_height + self.board.cell_height // 2
        radius = (self.board.cell_width // 2) - self.board.padding

        # Check if the click is within the piece's circle
        if (mouse_x - piece_x) ** 2 + (mouse_y - piece_y) ** 2 <= radius ** 2:
            # Set dragging-related attributes
            self.board.selected_piece = (row, col)
            self.board.selected_piece_color = piece_color
            self.board.drag_offset_x = mouse_x - piece_x
            self.board.drag_offset_y = mouse_y - piece_y
            return True  # Indicate that a piece was selected

        return False  # No piece was selected



    def handle_mousedown(self, event):
        for row in range(8):
            for col in range(8):
                piece_color = self.data[row][col]  # Get the color from the board
                if piece_color in ['red']:
                    if self.select_piece(event, row, col, piece_color):
                        self.possible_moves = [
                            (self.selected_piece[0] - 1, self.selected_piece[1] - 1),  # Top left
                            (self.selected_piece[0] - 1, self.selected_piece[1] + 1),  # Top right
                        ]
                        print('Potential moves: ', self.possible_moves)
                        self.handle_move(row, col)
                elif piece_color in ['rking']:
                    if self.select_piece(event, row, col, piece_color):
                        self.possible_moves = [
                            (self.selected_piece[0] - 1, self.selected_piece[1] - 1),  # Top left
                            (self.selected_piece[0] - 1, self.selected_piece[1] + 1),  # Top right
                            (self.selected_piece[0] + 1, self.selected_piece[1] - 1),  # Top left
                            (self.selected_piece[0] + 1, self.selected_piece[1] + 1),  # Top right
                        ]
                        self.handle_move(row, col)
                    

    

    def handle_move(self, row, col):
        # Check if within bounds and empty
        for move in self.possible_moves:
            target_row, target_col = move
            if 0 <= target_row < 8 and 0 <= target_col < 8:  # Check within boundaries
                if self.data[target_row][target_col] is None:
                    self.regular_moves.append((target_row, target_col))  # Append as tuple
                    self.valid_moves.append((target_row, target_col))
                    print('Regular moves mousedown: ', self.regular_moves)
                # Check if target square contains an opponent's piece
                elif self.data[target_row][target_col] in ['black', 'bking']:

                    # Calculate the landing square for a capture
                    landing_row = target_row - (row - target_row)  # Mirror target_row
                    landing_col = target_col - (col - target_col)  # Mirror target_col

                    # Ensure landing square is within bounds and empty
                    if (
                            0 <= landing_row < 8
                            and 0 <= landing_col < 8
                            and self.data[landing_row][landing_col] is None
                    ):
                        self.valid_moves.append((landing_row, landing_col))  # Add to vaild moves
                        self.capture_moves.append((landing_row, landing_col))  # Add to capture moves
                        self.capture_piece = [target_row, target_col]  # Save opponent's piece location
                        print('Capture moves mousedown: ', self.capture_moves)
                        break


'''
