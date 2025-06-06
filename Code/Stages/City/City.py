import pygame
import sys

class City:
    def __init__(self, game, pos, save):
        self.game = game
        self.pos = pos
        self.save = save
    def run(self):
        print("City!")
        pygame.quit()
        sys.exit()
        pass