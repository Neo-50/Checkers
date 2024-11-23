import pygame


def draw_lines(window, colors, start_x, start_y, end_x, end_y):
    # Draw the lines
    pygame.draw.line(window, colors['white'], (start_x, start_y),
                     (end_x, end_y))


def draw_gamepiece(window, row, col, cell_width, cell_height, color, radius):
    # Draw gamepieces
    center_x = col * cell_width + cell_width // 2
    center_y = row * cell_height + cell_height // 2
    pygame.draw.circle(window, color, (center_x, center_y), radius)


def handle_mousedown(event, tset):
    # Handles the MOUSEBUTTONDOWN event, selecting a piece.
    mouse_x, mouse_y = event.pos
    for row in range(8):
        for col in range(8):
            if tset.board[row][col] in ['black', 'red']:
                piece_x = col * tset.cell_width + tset.cell_width // 2
                piece_y = row * tset.cell_height + tset.cell_height // 2
                radius = (tset.cell_width // 2) - tset.padding

                # Check if click is within the piece's circle
                if (mouse_x - piece_x) ** 2 + (mouse_y - piece_y) ** 2 <= radius ** 2:
                    tset.dragging_piece = (row, col)
                    tset.drag_offset_x = mouse_x - piece_x
                    tset.drag_offset_y = mouse_y - piece_y
                    break


def handle_mousemotion(event, tset):
    # Handles MOUSEMOTION event, updating piece position while dragging.
    if tset.dragging_piece:
        # Get the mouse position during dragging
        mouse_x, mouse_y = pygame.mouse.get_pos()
        new_x = mouse_x - tset.drag_offset_x
        new_y = mouse_y - tset.drag_offset_y

        # Draw the piece at the new position
        pygame.draw.circle(tset.window, tset.colors['black'], (new_x, new_y), tset.radius)


def handle_mouseup(event, tset):
    # Handles MOUSEBUTTONUP event, finalizing the piece move.
    if tset.dragging_piece:
        mouse_x, mouse_y = event.pos
        target_col = mouse_x // tset.cell_width
        target_row = mouse_y // tset.cell_height

        # Validate move
        if 0 <= target_col < 8 and 0 <= target_row < 8:
            # Update the board (or implement your move logic here)
            tset.board[tset.dragging_piece[0]][tset.dragging_piece[1]] = None
            tset.board[target_row][target_col] = 'black'  # Or 'red', depending on the piece

        tset.dragging_piece = None  # Reset dragging state
