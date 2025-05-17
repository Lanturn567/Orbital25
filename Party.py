import sys
import pygame

class Party:
    def __init__(self, game, start_pos):
        self.game = game
        self.start_pos = start_pos

    def run(self):
        print("The Party Begins...")
        pygame.quit()
        sys.exit()
        pass