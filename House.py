import sys
import pygame

class House:
    def __init__(self, game, start_pos):
        self.game = game
        self.start_pos = start_pos

    def run(self):
        print("Im Back...")
        pygame.quit()
        sys.exit()
        pass