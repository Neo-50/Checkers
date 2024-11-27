import pygame
from random import choice


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
            piece_color = tset.board[row][col]  # Get the color from the board
            if piece_color in ['red']:
                piece_x = col * tset.cell_width + tset.cell_width // 2
                piece_y = row * tset.cell_height + tset.cell_height // 2
                radius = (tset.cell_width // 2) - tset.padding

                # Check if click is within the piece's circle
                if (mouse_x - piece_x) ** 2 + (mouse_y - piece_y) ** 2 <= radius ** 2:
                    tset.dragging_piece = (row, col)
                    tset.dragged_piece_color = piece_color  # Save the piece's color
                    tset.drag_offset_x = mouse_x - piece_x
                    tset.drag_offset_y = mouse_y - piece_y
                    break


def handle_mousemotion(tset):
    # Handles MOUSEMOTION event, updating piece position while dragging.
    if tset.dragging_piece:
        # Get the mouse position during dragging
        mouse_x, mouse_y = pygame.mouse.get_pos()
        new_x = mouse_x - tset.drag_offset_x
        new_y = mouse_y - tset.drag_offset_y

        # Draw the piece at the new position
        pygame.draw.circle(tset.window, tset.colors[tset.dragged_piece_color], (new_x, new_y), tset.radius)


def handle_mouseup(event, tset):
    for row in tset.board:
        print(row)

    # Handles MOUSEBUTTONUP event, finalizing the piece move.
    if tset.dragging_piece:
        mouse_x, mouse_y = event.pos
        target_col = mouse_x // tset.cell_width
        target_row = mouse_y // tset.cell_height

        # Validate move
        if 0 <= target_col < 8 and 0 <= target_row < 8:
            # Define list of valid moves
            valid_moves = [
                (tset.dragging_piece[0] - 1, tset.dragging_piece[1] - 1),  # Forward left corner
                (tset.dragging_piece[0] - 1, tset.dragging_piece[1] + 1),  # Forward right corner
            ]
            # Check if the target square is one of the valid moves
            if (target_row, target_col) in valid_moves:
                # Check if target square is not occupied
                if tset.board[target_row][target_col] is None:
                    # Update the board
                    tset.board[tset.dragging_piece[0]][tset.dragging_piece[1]] = None
                    tset.board[target_row][target_col] = tset.dragged_piece_color

        tset.dragging_piece = None  # Reset dragging state


def draw_dragged_piece(window, mouse_x, mouse_y, tset):
    # Draws the piece being dragged at the mouse position.
    new_x = mouse_x - tset.drag_offset_x
    new_y = mouse_y - tset.drag_offset_y
    pygame.draw.circle(window, tset.colors[tset.dragged_piece_color], (new_x, new_y), tset.radius)


def ai_move(tset):
    for row in tset.board:
        print(row)

    """AI move function to update the board with AI's move."""

    ai_moves = []  # List to store valid moves

    # Loop through the board to find AI pieces ('red')
    for row in range(8):
        for col in range(8):
            if tset.board[row][col] == 'black':  # AI's pieces
                potential_moves = [
                    (row + 1, col - 1),  # Forward-left
                    (row + 1, col + 1),  # Forward-right
                ]
                for target_row, target_col in potential_moves:
                    # Ensure within bounds and target square is empty
                    if 0 <= target_row < 8 and 0 <= target_col < 8:
                        if tset.board[target_row][target_col] is None:
                            ai_moves.append(((row, col), (target_row, target_col)))
                            print(ai_moves)

    if not ai_moves:
        print("No valid moves for AI!")
        return

    # Randomly select a valid move
    move = choice(ai_moves)
    start, end = move
    tset.board[start[0]][start[1]] = None  # Remove piece from start position
    tset.board[end[0]][end[1]] = 'black'  # Place piece in target position


