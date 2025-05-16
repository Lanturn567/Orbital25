import sys
import pygame

class Gym:
    def __init__(self, game, start_pos):
        self.game = game
        self.start_pos = start_pos

    def run(self):
        print("Challenging...")
        pygame.quit()
        sys.exit()
        pass