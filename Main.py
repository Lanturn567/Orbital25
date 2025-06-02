from Code.Opening.Opening import *

if __name__ == "__main__":
    game = Opening()
    nextStage = game.run()
    while True:
        nextStage = checkExit(nextStage)