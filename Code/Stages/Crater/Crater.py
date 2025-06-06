import pygame
import sys

class Crater:
    def __init__(self, game, start_pos, save):
        self.game = game
        self.pos = start_pos
        self.save = save
    def run(self):
        print("Thanks for Playing! To the next milestone!")
        pygame.quit()
        sys.exit()
        pass