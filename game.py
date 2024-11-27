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
                    self.handle_mousemotion()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouseup(event)
                    self.player_turn = False

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
                        break

    def handle_mousemotion(self):
        if self.board.dragging_piece:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            new_x = mouse_x - self.board.drag_offset_x
            new_y = mouse_y - self.board.drag_offset_y
            self.board.draw_circle(new_x, new_y, self.board.dragged_piece_color)

    def handle_mouseup(self, event):
        if self.board.dragging_piece:
            mouse_x, mouse_y = event.pos
            
            target_col = mouse_x // self.board.cell_width
            target_row = mouse_y // self.board.cell_height

            # Validate move
            if 0 <= target_col < 8 and 0 <= target_row < 8:
                # Define list of valid moves
                valid_moves = [
                    (self.board.dragging_piece[0] - 1, self.board.dragging_piece[1] - 1),  # Forward left corner
                    (self.board.dragging_piece[0] - 1, self.board.dragging_piece[1] + 1),  # Forward right corner
                ]
                # Check if the target square is one of the valid moves
                if (target_row, target_col) in valid_moves:
                    # Check if target square is not occupied
                    if self.board.data[target_row][target_col] is None:
                        # Update the board
                        self.board.data[self.board.dragging_piece[0]][self.board.dragging_piece[1]] = None
                        self.board.data[target_row][target_col] = self.board.dragged_piece_color

            self.board.dragging_piece = None  # Reset dragging state

