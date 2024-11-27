import pygame
from settings import Settings
import functions as gf


def run_game():
    # Initialize pygame and settings
    pygame.init()
    tset = Settings()

    # Set the title of the window and fill with gray color
    pygame.display.set_caption("Checkers")

    running = True

    while running:
        # Clear the screen
        tset.window.fill((200, 200, 200))

        # Draw the board lines (vertical and horizontal)
        for vline in range(1, 8):
            gf.draw_lines(tset.window, tset.colors, getattr(tset, f'vline{vline}_start_x'),
                          getattr(tset, f'vline{vline}_start_y'), getattr(tset, f'vline{vline}_end_x'),
                          getattr(tset, f'vline{vline}_end_y'))

        for hline in range(1, 8):
            gf.draw_lines(tset.window, tset.colors, getattr(tset, f'hline{hline}_start_x'),
                          getattr(tset, f'hline{hline}_start_y'), getattr(tset, f'hline{hline}_end_x'),
                          getattr(tset, f'hline{hline}_end_y'))

        # Draw non-dragged pieces
        for row in range(8):
            for col in range(8):
                if tset.board[row][col] == 'black':
                    gf.draw_gamepiece(tset.window, row, col, tset.cell_width,
                                    tset.cell_height, tset.colors['black'], tset.radius)
                elif tset.board[row][col] == 'red':
                    gf.draw_gamepiece(tset.window, row, col, tset.cell_width,
                                    tset.cell_height, tset.colors['red'], tset.radius)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif tset.player_turn:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    gf.handle_mousedown(event, tset)
                elif event.type == pygame.MOUSEMOTION:
                    gf.handle_mousemotion(tset)
                elif event.type == pygame.MOUSEBUTTONUP:
                    gf.handle_mouseup(event, tset)
                    tset.player_turn = False

        # Draw the dragged piece, if any
        if tset.dragging_piece:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            gf.draw_dragged_piece(tset.window, mouse_x, mouse_y, tset)

        # AI's turn
        if not tset.player_turn:  # Process AI logic only once per frame
            gf.ai_move(tset)
            tset.player_turn = True  # Switch back to player's turn

        # Update the display
        pygame.display.flip()

        # Set the framerate
        pygame.time.Clock().tick(60)


run_game()
