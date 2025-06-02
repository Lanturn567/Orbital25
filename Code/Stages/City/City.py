import pygame
import sys

class City:
    def __init__(self, game, pos):
        self.game = game
        self.pos = pos
    def run(self):
        print("City!")
        pygame.quit()
        sys.exit()
        pass