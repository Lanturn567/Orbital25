from Code.Opening.Opening import *
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    game = Opening()
    pygame.display.set_caption("Pokemon DLKL")
    surface = pygame.image.load(os.path.join(BASE_DIR, "./Assets/Pokemon/DanielRight.png"))
    pygame.display.set_icon(surface)
    nextStage = game.run()
    while True:
        nextStage = checkExit(nextStage)