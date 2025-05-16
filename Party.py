import sys
import pygame

class Party:
    def __init__(self, game, start_pos):
        self.game = game
        self.start_pos = start_pos

    def run(self):
        print("Going Left...")
        pygame.quit()
        sys.exit()
        pass