import sys
import pygame

class Mountain:
    def __init__(self, game, start_pos):
        self.game = game
        self.start_pos = start_pos

    def run(self):
        print("To the Mountains...")
        pygame.quit()
        sys.exit()
        pass