import pygame
from board import Board

'''
Responsibilies: 
    1. Deal with pygame stuff - initialization, configuration, rendering lifecyle
    2. Deal with operating system stuff - mouse events
    3. Game loop - start() method
'''


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Checkers")
        self.board = Board()
        self.running = True
        self.player_turn = True
        self.possible_moves = []
        self.regular_moves = []
        self.valid_moves = []
        self.capture_moves = []
        self.capture_piece = []

    def start(self):
        while self.running:
            self.board.draw(self.valid_moves)
            self.handle_events()
            if not self.player_turn:
                self.board.draw(self.valid_moves)
                pygame.display.flip()  # Update the screen after player's turn
                pygame.time.wait(500)  # Add a small delay for better pacing
                self.board.ai_move()
                self.board.draw(self.valid_moves)
                pygame.display.flip()
                pygame.time.wait(500)
                self.player_turn = True  # Switch back to the player's turn
            pygame.display.flip()
            pygame.time.Clock().tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if self.player_turn:   # Event Listeners
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mousedown(event)
                elif event.type == pygame.MOUSEMOTION:
                    if self.board.selected_piece:
                        self.board.draw_dragging_piece()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouseup(event)
                    self.valid_moves = []
                    pygame.time.wait(100)

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
                piece_color = self.board.data[row][col]  # Get the color from the board
                if piece_color in ['red']:
                    if self.select_piece(event, row, col, piece_color):
                        self.possible_moves = [
                            (self.board.selected_piece[0] - 1, self.board.selected_piece[1] - 1),  # Top left
                            (self.board.selected_piece[0] - 1, self.board.selected_piece[1] + 1),  # Top right
                        ]
                        self.handle_move(row, col)
                elif piece_color in ['rking']:
                    if self.select_piece(event, row, col, piece_color):
                        self.possible_moves = [
                            (self.board.selected_piece[0] - 1, self.board.selected_piece[1] - 1),  # Top left
                            (self.board.selected_piece[0] - 1, self.board.selected_piece[1] + 1),  # Top right
                            (self.board.selected_piece[0] + 1, self.board.selected_piece[1] - 1),  # Top left
                            (self.board.selected_piece[0] + 1, self.board.selected_piece[1] + 1),  # Top right
                        ]
                        self.handle_move(row, col)

    def handle_move(self, row, col):
        # Check if within bounds and empty
        for move in self.possible_moves:
            target_row, target_col = move
            if 0 <= target_row < 8 and 0 <= target_col < 8:  # Check within boundaries
                if self.board.data[target_row][target_col] is None:
                    self.regular_moves.append((target_row, target_col))  # Append as tuple
                    self.valid_moves.append((target_row, target_col))
                # Check if target square contains an opponent's piece
                elif self.board.data[target_row][target_col] in ['black', 'bking']:

                    # Calculate the landing square for a capture
                    landing_row = target_row - (row - target_row)  # Mirror target_row
                    landing_col = target_col - (col - target_col)  # Mirror target_col

                    # Ensure landing square is within bounds and empty
                    if (
                            0 <= landing_row < 8
                            and 0 <= landing_col < 8
                            and self.board.data[landing_row][landing_col] is None
                    ):
                        self.valid_moves.append((landing_row, landing_col))  # Add to vaild moves
                        self.capture_moves.append((landing_row, landing_col))  # Add to capture moves
                        self.capture_piece = [target_row, target_col]  # Save opponent's piece location
                        break

    def handle_mouseup(self, event):
        if self.board.selected_piece:
            mouse_x, mouse_y = event.pos

            target_col = mouse_x // self.board.cell_width
            target_row = mouse_y // self.board.cell_height

            if (target_row, target_col) in self.regular_moves:
                # Clear old position
                self.board.data[self.board.selected_piece[0]][self.board.selected_piece[1]] = None
                # King if end of board
                if target_row == 0:
                    self.board.selected_piece_color = 'rking'
                # Set new position
                self.board.data[target_row][target_col] = self.board.selected_piece_color
                self.player_turn = False  # Change turn flag

            if (target_row, target_col) in self.capture_moves:
                # Clear old position
                self.board.data[self.board.selected_piece[0]][self.board.selected_piece[1]] = None
                # King if end of board
                if target_row == 0:
                    self.board.selected_piece_color = 'rking'
                # Set new position
                self.board.data[target_row][target_col] = self.board.selected_piece_color
                pygame.time.wait(300)
                # Clear opponent piece
                self.board.data[self.capture_piece[0]][self.capture_piece[1]] = None

                # Increase score, end turn
                self.board.player_score += 1

                print(f'Player captured piece at {self.capture_piece}. \n'
                      f'Contents of cell at captured piece location: '
                      f'{self.board.data[self.capture_piece[0]][self.capture_piece[1]]} \n'
                      f'Player score is now: {self.board.player_score}')

                self.player_turn = False  # Change turn flag

        self.board.selected_piece = None  # Reset dragging state
