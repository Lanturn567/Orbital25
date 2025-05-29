import pygame
import sys

class City:
    def __init__(self, game):
        self.game = game
    def run(self):
        print("City!")
        pygame.quit()
        sys.exit()
        pass