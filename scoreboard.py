import pygame

from constants import *
from vector import Vector

FONT = 'Arial'
FONT_SIZE = 20
PADDING = 10

class Scoreboard:
    def __init__(self, window, origin = Vector(0, 0)):
        self.window = window
        self.origin = origin 
        self.player_score = 0
        self.computer_score = 0
    
    def draw(self):
        font = pygame.font.SysFont(FONT, FONT_SIZE)

        score_text = font.render(f'Player: {self.player_score}    |    AI: {self.computer_score}', True, COLORS['black'])
        title_text = font.render('Checkers', True, COLORS['black'])

        score_text_width = score_text.get_width()

        score_text_x = self.window.get_width() - score_text_width - PADDING
        score_text_y = PADDING

        self.window.blit(score_text, (score_text_x, score_text_y))
        self.window.blit(title_text, (PADDING, score_text_y))

    def increment_player_score(self):
        self.player_score = self.player_score + 1
    
    def increment_computer_score(self):
        self.computer_score = self.computer_score + 1