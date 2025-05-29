import pygame
import random
import sys
import os
from Code.LevelTwoStage.LevelTwo import Entity, TEXT_BUTTON, ANIM_SPEED
from Code.LevelTwoStage.StoryTextBox import StoryTextBox
from Code.Entities.Database import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BLOCK_SIZE = 32
PLAYER_SIZE = (32, 64)
DOWN, LEFT, RIGHT, UP = 2, 0, 1, 3
dirs = {"left" : LEFT,
        "right" : RIGHT,
        "up" : UP,
        "down" : DOWN}
INTERACTABLE_BOUNDS = [2 * BLOCK_SIZE, 2 * BLOCK_SIZE]
ITEM_PATHS = { "fake" : [os.path.join(BASE_DIR, '../../Assets/Pokemon/fake.png')],
               "real" : [os.path.join(BASE_DIR, '../../Assets/Pokemon/real.png')],
}
ANIM_SPEED = 4
ANIM_DIST = 3
AFTER_EVENT_DELAY = 2


class Item(Entity):

    assets = {}
    ini = False

    def __init__(self, pos, groups, game, size, name, type="default", z=2):
        if not Item.ini:
            Item.init_assets(ITEM_PATHS)  # Reuse same assets, or create ITEM_PATHS
            Item.ini = True
        super().__init__(pos, groups, size, z)
        self.game = game
        self.name = name
        self.images = Item.assets.get(type, [[pygame.Surface(size)] * 4] * 4)
        self.image = self.images[DOWN][0]  # Show default direction
        self.rect.center = pos
        self.hitbox.center = (self.x, self.y + PLAYER_SIZE[1] // 4)

        # Text handling
        self.info = database[name]
        text = self.info.get("talk")
        self.text = text if text else ["You found something!"]
        self.currText = 0
        self.maxTalks = len(self.text)
        self.inEvent = False
        self.eventDone = False
        self.delayAfterEvent = 0
        self.box = pygame.Rect(self.x, self.y, INTERACTABLE_BOUNDS[0], INTERACTABLE_BOUNDS[1])
        self.box.center = (self.x, self.y)

    @classmethod
    def init_assets(cls, database):
        for key in database:
            paths = database[key]
            try:
                surface = pygame.image.load(paths[0])
            except FileNotFoundError:
                surface = pygame.Surface((32, 32))
                surface.fill((255, 255, 255))

            # One frame reused for all directions (LEFT, RIGHT, DOWN, UP)
            frame = surface.subsurface(pygame.Rect(0, 0, 32, 32))
            cls.assets[key] = [[frame] * 4] * 4

    def update(self, dt):
        self.delayAfterEvent += 0 if self.delayAfterEvent >= AFTER_EVENT_DELAY else dt * ANIM_SPEED
        self.rect.center = (self.x, self.y)
        self.hitbox.center = (self.x, self.y + PLAYER_SIZE[1] // 4)
        if self.eventDone:
            self.kill()
        elif not self.inEvent and self.game.textComplete:
            self.image = self.images[DOWN][0]
        elif self.inEvent and self.game.textComplete:
            self.eventDone = True
            self.inEvent = False
            self.game.inEvent = False
            self.delayAfterEvent = 0


    def collide(self):
        keys = pygame.key.get_pressed()
        if self.box.colliderect(self.game.player.hitbox) and keys[pygame.K_SPACE] and not self.inEvent and self.delayAfterEvent >= AFTER_EVENT_DELAY:
            self.inEvent = True
            self.game.inEvent = True
            self.makeEvent()

    def makeEvent(self):
        StoryTextBox.init__text(self.text[self.currText] if self.text[self.currText].endswith(".txt") else self.text)
        self.game.buttons[TEXT_BUTTON].reset()
        self.currText = self.currText + 1 if self.currText < self.maxTalks - 1 else self.currText

