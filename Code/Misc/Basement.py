import sys
import pygame

class Basement:
    def __init__(self, game, start_pos):
        self.game = game
        self.start_pos = start_pos

    def run(self):
        print("Creepy...")
        pygame.quit()
        sys.exit()
        pass