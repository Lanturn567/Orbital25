import random
import pygame
import Audio

class ToneMatrix:

    def __init__(self):
        self.notes = []
        for i in range(16):
            self.notes.append(Note(i))

        self.seq = []
        for i in range(16):
            next = random.randint(-7, 15)
            if next >= 0:
                self.seq.append(self.notes[next])
            else:
                self.seq.append(None)

    def song(self):
        for i in range(16):
            next = random.randint(-7, 15)
            if next >= 0:
                self.seq[i] = self.notes[next]
            else:
                self.seq[i] = None



class Note:
    def __init__(self, i):
        self.sound = pygame.mixer.Sound("../../Audio/note" + str(i + 1) + ".wav")


