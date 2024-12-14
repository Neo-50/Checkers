import pygame
from board import Board

from constants import *

class Game:
    def __init__(self):
        self.init_pygame()
        self.board = Board(self.window)
        self.running = True

    def init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Checkers")
        self.window = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT + 50))

    def start(self):
        while self.running:
            self.handle_events()
            self.board.update()
            self.board.draw()
            pygame.display.flip()
            pygame.time.Clock().tick(60)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            self.board.handle_event(event)
