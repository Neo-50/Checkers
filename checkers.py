import pygame
from settings import Settings
import functions as gf


def run_game():
    # Initialize pygame and settings
    pygame.init()
    tset = Settings()

    # Set the title of the window
    pygame.display.set_caption("Checkers")

    running = True
    # player_turn = True

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                gf.handle_mousedown(event, tset)
            elif event.type == pygame.MOUSEMOTION:
                gf.handle_mousemotion(event, tset)
            elif event.type == pygame.MOUSEBUTTONUP:
                gf.handle_mouseup(event, tset)

        '''
        # AI's turn
        if not player_turn:  # Process AI logic only once per frame
            gf.ai_move(tset.board)
            player_turn = True  # Switch back to player's turn

        # Check for a winner or tie
        if gf.victory(tset.board):
            print("Game Over! Winner detected.")
            running = False
        '''

        tset.window.fill((200, 200, 200))

        # Draw vertical lines
        gf.draw_lines(tset.window, tset.colors, tset.vline1_start_x,
                      tset.vline1_start_y, tset.vline1_end_x, tset.vline1_end_y)
        gf.draw_lines(tset.window, tset.colors, tset.vline2_start_x,
                      tset.vline2_start_y, tset.vline2_end_x, tset.vline2_end_y)
        gf.draw_lines(tset.window, tset.colors, tset.vline3_start_x,
                      tset.vline3_start_y, tset.vline3_end_x, tset.vline3_end_y)
        gf.draw_lines(tset.window, tset.colors, tset.vline4_start_x,
                      tset.vline4_start_y, tset.vline4_end_x, tset.vline4_end_y)
        gf.draw_lines(tset.window, tset.colors, tset.vline5_start_x,
                      tset.vline5_start_y, tset.vline5_end_x, tset.vline5_end_y)
        gf.draw_lines(tset.window, tset.colors, tset.vline6_start_x,
                      tset.vline6_start_y, tset.vline6_end_x, tset.vline6_end_y)
        gf.draw_lines(tset.window, tset.colors, tset.vline7_start_x,
                      tset.vline7_start_y, tset.vline7_end_x, tset.vline7_end_y)

        # Draw horizontal lines
        gf.draw_lines(tset.window, tset.colors, tset.hline1_start_x,
                      tset.hline1_start_y, tset.hline1_end_x, tset.hline1_end_y)
        gf.draw_lines(tset.window, tset.colors, tset.hline2_start_x,
                      tset.hline2_start_y, tset.hline2_end_x, tset.hline2_end_y)
        gf.draw_lines(tset.window, tset.colors, tset.hline3_start_x,
                      tset.hline3_start_y, tset.hline3_end_x, tset.hline3_end_y)
        gf.draw_lines(tset.window, tset.colors, tset.hline4_start_x,
                      tset.hline4_start_y, tset.hline4_end_x, tset.hline4_end_y)
        gf.draw_lines(tset.window, tset.colors, tset.hline5_start_x,
                      tset.hline5_start_y, tset.hline5_end_x, tset.hline5_end_y)
        gf.draw_lines(tset.window, tset.colors, tset.hline6_start_x,
                      tset.hline6_start_y, tset.hline6_end_x, tset.hline6_end_y)
        gf.draw_lines(tset.window, tset.colors, tset.hline7_start_x,
                      tset.hline7_start_y, tset.hline7_end_x, tset.hline7_end_y)

        for row in range(8):
            for col in range(8):
                if tset.board[row][col] == 'black':
                    gf.draw_gamepiece(tset.window, row, col, tset.cell_width,
                                    tset.cell_height, tset.colors['black'], tset.radius)
                elif tset.board[row][col] == 'red':
                    gf.draw_gamepiece(tset.window, row, col, tset.cell_width,
                                    tset.cell_height, tset.colors['red'], tset.radius)

        # Update the display
        pygame.display.flip()

        # Set the framerate
        pygame.time.Clock().tick(10)


run_game()
