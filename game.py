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
        self.board = Board()
        self.running = True
        self.player_turn = True
        self.init_pygame()

    def init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Checkers")

    def start(self):
        while self.running:
            self.board.draw()
            self.handle_events()
            self.ai_move()
            pygame.display.flip()
            pygame.time.Clock().tick(60)

    def ai_move(self):
        if not self.player_turn:  # Process AI logic only once per frame
            self.board.ai_move()
            self.player_turn = True  # Switch back to player's turn

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.player_turn:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mousedown(event)
                elif event.type == pygame.MOUSEMOTION:
                    if self.board.dragging_piece:
                        self.board.draw_dragging_piece()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouseup(event)

    def handle_mousedown(self, event):
        mouse_x, mouse_y = event.pos
        for row in range(8):
            for col in range(8):
                piece_color = self.board.data[row][col]  # Get the color from the board
                if piece_color in ['red']:
                    piece_x = col * self.board.cell_width + self.board.cell_width // 2
                    piece_y = row * self.board.cell_height + self.board.cell_height // 2
                    radius = (self.board.cell_width // 2) - self.board.padding

                    # Check if click is within the piece's circle
                    if (mouse_x - piece_x) ** 2 + (mouse_y - piece_y) ** 2 <= radius ** 2:
                        self.board.dragging_piece = (row, col)
                        self.board.dragged_piece_color = piece_color  # Save the piece's color
                        self.board.drag_offset_x = mouse_x - piece_x
                        self.board.drag_offset_y = mouse_y - piece_y
                        print(f"Offsets: ({self.board.drag_offset_x}, {self.board.drag_offset_y})")
                        break

    def handle_mouseup(self, event):
        if self.board.dragging_piece:
            mouse_x, mouse_y = event.pos

            target_col = mouse_x // self.board.cell_width
            target_row = mouse_y // self.board.cell_height

            # Validate move
            if 0 <= target_col < 8 and 0 <= target_row < 8:
                valid_moves = [
                    (self.board.dragging_piece[0] - 1, self.board.dragging_piece[1] - 1),
                    (self.board.dragging_piece[0] - 1, self.board.dragging_piece[1] + 1),
                ]
                if (target_row, target_col) in valid_moves:
                    if self.board.data[target_row][target_col] is None:
                        self.board.data[self.board.dragging_piece[0]][self.board.dragging_piece[1]] = None
                        self.board.data[target_row][target_col] = self.board.dragged_piece_color
                        self.player_turn = False
            print(f"Releasing piece at: ({target_row}, {target_col})")

        self.board.dragging_piece = None  # Reset dragging state
