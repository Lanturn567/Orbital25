import random
import pygame

class ToneMatrix:

    def __init__(self):
        self.notes = []
        for i in range(16):
            curr = []
            for j in range(16):
                curr.append(Note(i))
            self.notes.append(curr)

    def song(self):
        for i in range(16):
            set = False
            for j in range(16):
                if random.randint(0, 10) < 1 and set == False:
                    self.notes[i][j].play = True
                    set = True
            self.notes[i][i].play = True if set == False else False

class Note:

    def __init__(self, i):
        self.sound = pygame.mixer.Sound("./music/note" + str(i + 1) + ".wav")
        self.play = False


