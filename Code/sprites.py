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
from Code.Save import *
from random import uniform
from Code.support import draw_bar
from Code.timer import Timer

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
POKEMON_SIZE = (64, 64)
DELAY_AFTER_CLICK = 4
TEXT_BOX_POS = (65, MAX_Y - 140)
TEXT_BUTTON, VOLUME_BUTTON = 1, 0
DELAY_AT_START = 55
WARP_SOUND_PATH = os.path.join(BASE_DIR, "../Audio/Warp.wav")
MAX_ALPHA = 255
FINAL_DELAY = 5

SURF_TEXT_PATH = os.path.join(BASE_DIR, "./EventText/Surf.txt")
NO_SURF_TEXT_PATH = os.path.join(BASE_DIR, "./EventText/NoSurf.txt")


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
        tall_sprites = sorted([sprite for sprite in self if sprite.z == 5], key=lambda sprite: sprite.y_sort)



        for lis in (bg_sprites, water_sprites, base_sprites, tree_sprites, wall_sprites, tall_sprites):
            for sprite in lis:
                x, y = sprite.rect.topleft
                self.surf.blit(sprite.image, (x + self.offsetX, y + self.offsetY))

class BattleSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

    def draw(self, current_pokemon_sprite):
        for sprite in sorted(self, key = lambda sprite: sprite.z):
            if sprite.z == BATTLE_LAYERS['outline']:
                if sprite.pokemon_sprite == current_pokemon_sprite:
                    self.display_surface.blit(sprite.image, sprite.rect)
            else:
                self.display_surface.blit(sprite.image, sprite.rect)

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

    def __init__(self, pos, stage, image, groups, game, loc, z=1):
        super().__init__(pos, image, groups, z)
        self.game = game
        self.stage = stage
        self.loc = loc
        self.hitbox = pygame.Rect(self.rect.x + self.rect.width // 4, self.rect.y + self.rect.height // 4, self.rect.width // 2, self.rect.height // 2)


    def warp(self):
        self.game.save.updateStage(self.stage.title())
        self.game.save.updatePos(self.loc)
        self.game.nextStage = True
        SaveSystem.write(self.game.save)
        BaseWarp.warpSound.play()

class EventWarp(BaseWarp):

    def __init__(self, pos, stage, image, groups, game, loc, cond, z=1):
        super().__init__(pos, stage, image, groups, game, loc, z)
        self.cond = cond
        self.eventDone = False

    def warp(self):
        if self.cond():
            super().warp()
        else:
            self.makeEvent()

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


class Event(Sprite):

    def __init__(self, pos, image, groups, game, z=0):
        super().__init__(pos, image, groups, z)
        self.game = game

    def event(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            #do something
            print("im eventing")
            #reset storytextbox
            #change game state


class Waterside(Event):
    tolerance = BLOCK_SIZE

    def event(self):
        if self.test():
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and self.game.water and self.game.player.moveWater():
                    StoryTextBox.init__text(NO_SURF_TEXT_PATH)
                    self.game.buttons[TEXT_BUTTON].reset()
                    #change game state
                    self.game.inEvent = True
                    self.game.water = False

            elif keys[pygame.K_SPACE] and not self.game.water and self.game.player.moveWater():
                StoryTextBox.init__text(SURF_TEXT_PATH)
                self.game.buttons[TEXT_BUTTON].reset()
                #change game state
                self.game.inEvent = True
                self.game.water = True

    def test(self):
        if self.game.player.facing == LEFT and self.game.player.x > self.rect.x and abs(self.game.player.y - self.rect.y) < Waterside.tolerance:
            return True
        elif self.game.player.facing == RIGHT and self.game.player.x < self.rect.x + Waterside.tolerance and abs(self.game.player.y - self.rect.y) < Waterside.tolerance:
            return True
        elif self.game.player.facing == UP and self.game.player.y > self.rect.y and abs(self.game.player.x- self.rect.x) < Waterside.tolerance:
            return True
        elif self.game.player.facing == DOWN and self.game.player.y < self.rect.y + Waterside.tolerance and abs(self.game.player.x - self.rect.x) < Waterside.tolerance:
            return True
        else:
            return False


class PokemonSprite(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, pokemon, index, pos_index, entity):
        # data
        self.index = index
        self.pos_index = pos_index
        self.entity = entity
        self.pokemon = pokemon
        self.frame_index, self.frames, self.state = 0, frames, 'idle'
        self.animation_speed = ANIMATION_SPEED + uniform(-1, 1)
        self.z = BATTLE_LAYERS['monster']
        self.highlight = False

        # sprite setup
        super().__init__(groups)
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_rect(center = pos)

        #timers
        self.timers = {
            'remove highlight': Timer(200, func = lambda: self.set_highlight(False))
        }

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        self.adjusted_frame_index = int(self.frame_index % len(self.frames[self.state]))
        self.image = self.frames[self.state][self.adjusted_frame_index]

        if self.highlight:
            white_surf = pygame.mask.from_surface(self.image).to_surface()
            white_surf.set_colorkey('black')
            self.image = white_surf

    def set_highlight(self, value):
        self.highlight = value
        if value:
            self.timers['remove highlight'].activate()

    def update(self, dt):
        for timer in self.timers.values():
            timer.update()
        self.animate(dt)
        self.pokemon.update(dt)

class PokemonNamesprite(pygame.sprite.Sprite):
    def __init__(self, pos, pokemon_sprite, groups, font):
        super().__init__(groups)
        self.pokemon_sprite = pokemon_sprite
        self.z = BATTLE_LAYERS['name']

        text_surf = font.render(pokemon_sprite.pokemon.name, False, COLORS['black'])
        padding = 10


        self.image = pygame.Surface((text_surf.get_width() + 2 * padding, text_surf.get_height() + 2 * padding))
        self.image.fill(COLORS['white'])
        self.image.blit(text_surf, (padding, padding))
        self.rect = self.image.get_rect(midtop=pos)


class PokemonLevelSprite(pygame.sprite.Sprite):
    def __init__(self, entity, pos, pokemon_sprite, groups, font):
        super().__init__(groups)
        self.pokemon_sprite = pokemon_sprite
        self.font = font
        self.z = BATTLE_LAYERS['name']

        self.image = pygame.Surface((60,26))
        self.rect = self.image.get_rect(topleft = pos) if entity == 'player' else self.image.get_rect(topright = pos)
        self.xp_rect = pygame.Rect(0,self.rect.height - 2,self.rect.width,2)

    def update(self, _):
        self.image.fill(COLORS['white'])

        text_surf = self.font.render(f'Lvl {self.pokemon_sprite.pokemon.level}', False, COLORS['black'])
        text_rect = text_surf.get_rect(center=(self.rect.width / 2, self.rect.height / 2))
        self.image.blit(text_surf, text_rect)

        draw_bar(self.image, self.xp_rect, self.pokemon_sprite.pokemon.xp, self.pokemon_sprite.pokemon.level_up, COLORS['black'], COLORS['white'], 0)

class PokemonStatsSprite(pygame.sprite.Sprite):
    def __init__(self, pos, pokemon_sprite, size, groups, font):
        super().__init__(groups)
        self.pokemon_sprite = pokemon_sprite
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect(midbottom = pos)
        self.font = font
        self.z = BATTLE_LAYERS['overlay']

    def update(self, _):
        self.image.fill(COLORS['white'])

        for index, (value, max_value) in enumerate(self.pokemon_sprite.pokemon.get_info()):
            color = (COLORS['red'], COLORS['blue'], COLORS['gray'])[index]
            if index < 2:  # health and energy
                text_surf = self.font.render(f'{int(value)}/{max_value}', False, COLORS['black'])
                text_rect = text_surf.get_rect(topleft=(self.rect.width * 0.05, index * self.rect.height / 2))
                bar_rect = pygame.Rect(text_rect.bottomleft + vector(0, -2), (self.rect.width * 0.9, 4))

                self.image.blit(text_surf, text_rect)
                draw_bar(self.image, bar_rect, value, max_value, color, COLORS['black'], 2)
            else:  # initiative
                init_rect = pygame.Rect((0, self.rect.height - 2), (self.rect.width, 2))
                draw_bar(self.image, init_rect, value, max_value, color, COLORS['white'], 0)

class PokemonOutlineSprite(pygame.sprite.Sprite):
    def __init__(self, pokemon_sprite, groups, frames):
        super().__init__(groups)
        self.z = BATTLE_LAYERS['outline']
        self.pokemon_sprite = pokemon_sprite
        self.frames = frames

        self.image = self.frames[self.pokemon_sprite.state][self.pokemon_sprite.frame_index]
        self.rect = self.image.get_rect(center = self.pokemon_sprite.rect.center)

    def update(self, _):
        self.image = self.frames[self.pokemon_sprite.state][self.pokemon_sprite.adjusted_frame_index]