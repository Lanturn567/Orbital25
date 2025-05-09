import random
import pygame

class ToneMatrix:

    def __init__(self):
        self.notes = []
        for i in range(16):
            self.notes.append(Note(i))

        self.seq = []
        for i in range(16):
            self.seq.append(self.notes[random.randint(0, 15)])

    def song(self):

        for i in range(16):
            self.seq[i] = self.notes[random.randint(0, 15)]



class Note:

    def __init__(self, i):
        self.sound = pygame.mixer.Sound("./music/note" + str(i + 1) + ".wav")


