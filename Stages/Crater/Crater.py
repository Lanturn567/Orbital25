import pygame
import sys

class Crater:
    def __init__(self, game):
        self.game = game
    def run(self):
        print("Crater!")
        pygame.quit()
        sys.exit()
        pass