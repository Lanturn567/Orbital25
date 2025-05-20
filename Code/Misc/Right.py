import sys
import pygame

class Right:
    def __init__(self, game, start_pos):
        self.game = game
        self.start_pos = start_pos

    def run(self):
        print("Going Right...")
        pygame.quit()
        sys.exit()
        pass