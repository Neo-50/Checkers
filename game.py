import pygame
from board import Board

from constants import *

'''
Responsibilies: 
    1. Deal with pygame stuff - initialization, configuration, rendering lifecyle
    2. Deal with operating system stuff - mouse events
    3. Game loop - start() method
'''


class Game:
    def __init__(self):
        self.init_pygame()
        self.board = Board(self.window)
        self.running = True
        self.window = None

    def init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Checkers")
        self.window = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT + 50))

    def start(self):
        while self.running:
            self.handle_events()
            self.board.draw()
            pygame.display.flip()
            pygame.time.Clock().tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if self.board.player_turn:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.board.handle_mousedown(event)
                elif event.type == pygame.MOUSEMOTION:
                    if self.board.selected_piece:
                        self.board.draw_dragging_piece()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.board.handle_mouseup(event)
