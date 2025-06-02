import pygame
import sys
import math
import random
import os
from Code.support import *
from pytmx.util_pygame import load_pygame
from Code.LevelTwoStage.StoryTextBox import StoryTextBox
from Code.LevelOneStage.LevelOne import LevelOneVolumeButton, VOL_BUTTON_PATHS
from Code.Opening.Opening import BGAsset

# Constants
TMX_PATH = "../../../Data/TilemapsPNG/LevelTwo-TileMap.tmx"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
START_POS = "begin"
DOWN, LEFT, RIGHT, UP = 2, 0, 1, 3
BLOCK_SIZE = 32
ASSET_SIZE = 32
PLAYER_SIZE = (32, 64)
PLAYER_SPEED = BLOCK_SIZE // 2
MAX_SPEED = BLOCK_SIZE
MAX_X, MAX_Y = 740, 493
MAX_FPS = 60
LEVEL_TWO_MUSIC_PATH = "../../Audio/LevelTwoBGM.mp3"
FADE_LEVEL = 100
FADE_CHANGE_PER_FRAME = 3
WATER_PATHS = ['../../../Assets/Water/0.png', '../../../Assets/Water/1.png', '../../../Assets/Water/2.png', '../../../Assets/Water/3.png']
PLAYER_PATHS = ['../../../Assets/Players/Darnielle/walkLeft.png', '../../../Assets/Players/Darnielle/walkRight.png', '../../../Assets/Darnielle/walkFront.png', '../../../Assets/Darnielle/walkBack.png']
POKEMON_PATHS = ['../../../Assets/Pokemon/pokeL.png', '../../..Assets/Pokemon/poker.png']  # Assuming single image for simplicity
TREE_PATH = ['../../../Assets/Background/Tree.png']
LEAF_PATH = ['../../../Assets/Background/Leaf.png']
FURINA_PATHS = ['../../../Assets/Players/Furina/WalkLeftFurina.png', '../../../Assets/Players/Furina/WalkRightFurina.png']
FURINA_ROAD = [RIGHT, RIGHT, RIGHT, UP, RIGHT, UP, RIGHT, UP, RIGHT,
               RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT]

STAGES = {}
FURINA_SIZE = (48, 64)
FURINA_GO_SPEED = BLOCK_SIZE * 4
FURINA_PROD_TEXT = "LevelTwoWarpingWithoutFurina.txt"
FURINA_EVENT_PATH = "LevelTwoFurinaEvent.txt"
INTERACTABLE_BOUNDS = [BLOCK_SIZE, BLOCK_SIZE]

WATER_SPEED = 1
GAME_VOLUME = 0.3
ANIM_SPEED = 8
ANIM_DIST = 4
SWAY_SPEED = BLOCK_SIZE
SWAY_INTERVAL = 2
SWAY_LENGTH = BLOCK_SIZE
SWAY_DELAY = 15
FLOAT_SPEED = BLOCK_SIZE // 3
FLOAT_INTERVAL = 4
FLOAT_LENGTH = BLOCK_SIZE
DIST_FROM_PLAYER = BLOCK_SIZE * 15
POKEMON_CRY = "./Audio/Poke.wav"
POKEMON_SIZE = (64, 64)
DELAY_AFTER_CLICK = 4
TEXT_BOX_POS = (65, MAX_Y - 140)
TEXT_BUTTON, VOLUME_BUTTON = 1, 0
TEXT_PATH = "LevelTwoText.txt"
TEXT_BOX_PATHS = ["../../UI/TextBox.png", "../../UI/TextBoxArrow.png"]
DELAY_AT_START = 55
WARP_PATH = "../../Assets/Background/Warp.png"
WARP_SOUND_PATH = os.path.join(BASE_DIR, "../Audio/Warp.wav")
MAX_ALPHA = 255
FINAL_DELAY = 5

class AllSprites(pygame.sprite.LayeredUpdates):
    def __init__(self):
        super().__init__()
        self.surf = pygame.display.get_surface()
        self.offsetX = 0
        self.offsetY = 0

    def draw(self, center):
        self.offsetX = -(center[0] - MAX_X // 2)
        self.offsetY = -(center[1] - MAX_Y // 2)


        bg_sprites = sorted([sprite for sprite in self if sprite.z == 0], key=lambda sprite: sprite.y_sort)
        water_sprites = sorted([sprite for sprite in self if sprite.z == 1], key=lambda sprite: sprite.y_sort)
        base_sprites = sorted([sprite for sprite in self if sprite.z == 2], key=lambda sprite: sprite.y_sort)
        tree_sprites = sorted([sprite for sprite in self if sprite.z == 3], key=lambda sprite: sprite.y_sort)
        wall_sprites = sorted([sprite for sprite in self if sprite.z == 4], key=lambda sprite: sprite.y_sort)


        for lis in (bg_sprites, water_sprites, base_sprites, tree_sprites, wall_sprites):
            for sprite in lis:
                x, y = sprite.rect.topleft
                self.surf.blit(sprite.image, (x + self.offsetX, y + self.offsetY))

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, image, groups, z=0):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.y_sort = self.rect.centery - BLOCK_SIZE // 2
        self.hitbox = self.rect.copy()

class AnimatedSprite(Sprite):
    assets = []
    ini = False
    length = 0

    def __init__(self, pos, paths, groups, z=0):
        cls = self.__class__
        if not cls.ini:
            cls.init_assets(paths)
            cls.ini = True
        super().__init__(pos, cls.assets[0], groups, z)
        self.currImage = 0

    @classmethod
    def init_assets(cls, paths):
        cls.assets = []
        for path in paths:
            try:
                cls.assets.append(pygame.image.load(path))
            except FileNotFoundError:
                surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
                surface.fill((255, 255, 255))
                cls.assets.append(surface)
        cls.length = len(cls.assets)

    def update(self, dt, *args, **kwargs):
        cls = self.__class__
        self.currImage += WATER_SPEED * dt
        self.image = cls.assets[int(self.currImage) % cls.length]

class AnimatedSpriteFromSheet(Sprite):
    assets = []
    ini = False
    length = 0

    def __init__(self, pos, sheet, frame_rects, groups, z=0):
        cls = self.__class__
        if not cls.ini:
            cls.init_assets(sheet, frame_rects)
            cls.ini = True
        super().__init__(pos, cls.assets[0], groups, z)
        self.image = cls.assets[0]
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.currImage = 0

    @classmethod
    def init_assets(cls, sheet, frame_rects):
        cls.assets = []
        for rect in frame_rects:
            frame_surface = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
            frame_surface.blit(sheet, (0, 0), rect)
            cls.assets.append(frame_surface)
        cls.length = len(cls.assets)

    def update(self, dt, *args, **kwargs):
        cls = self.__class__
        self.currImage += WATER_SPEED * dt
        self.image = cls.assets[int(self.currImage) % cls.length]

class BaseWarp(Sprite):
    pygame.mixer.init()
    warpSound = pygame.mixer.Sound(WARP_SOUND_PATH)

    def __init__(self, pos, stage, image, groups, game, z=1):
        super().__init__(pos, image, groups, z)
        self.game = game
        self.stage = stage
        self.hitbox = pygame.Rect(self.rect.x + self.rect.width // 4, self.rect.y + self.rect.height // 4, self.rect.width // 2, self.rect.height // 2)


    def warp(self):
        #self.game.nextStage = STAGES.get(self.stage)(self.game.screen)
        BaseWarp.warpSound.play()

class EventWarp(BaseWarp):

    def __init__(self, pos, stage, image, groups, game, cond, z=1):
        super().__init__(pos, stage, image, groups, game, z)
        self.cond = cond
        self.eventDone = False


    def warp(self):
        """

        stage = STAGES.get(self.stage)(self.game.screen)
        if self.cond():
            self.game.nextStage = stage
        else:
            self.makeEvent()
        """
        super().warp()

    def makeEvent(self):
        pass

class FurinaWarp(EventWarp):

    def __init__(self, pos, stage, image, groups, game, cond, z=1):
        super().__init__(pos, stage, image, groups, game, cond, z)

    def makeEvent(self):
        StoryTextBox.init__text(FURINA_PROD_TEXT)
        self.game.buttons[TEXT_BUTTON].reset()
        self.game.poke.cry.play()
        self.game.player.x = self.rect.x
        self.game.player.y = self.rect.y
        self.game.inEvent = True
        self.afterEvent()

    def afterEvent(self):
        def checker():
            if self.game.textComplete:
                self.game.inEvent = False
                self.game.updateEvent = None
                self.game.player.x = self.rect.x - BLOCK_SIZE
                self.game.player.facing = LEFT

        self.game.updateEvent = checker