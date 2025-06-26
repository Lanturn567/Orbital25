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
from Code.sprites import *
from Code.Save import *
from Code.entities import *
from Code.support import *


# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMX_PATH = os.path.join(BASE_DIR, "../../Data/TilemapsPNG/LevelTwo-TileMap.tmx")
START_POS = "begin"
DOWN, LEFT, RIGHT, UP = 2, 0, 1, 3
BLOCK_SIZE = 32
ASSET_SIZE = 32
PLAYER_SIZE = (32, 64)
PLAYER_SPEED = BLOCK_SIZE // 12 * 5
MAX_SPEED = BLOCK_SIZE // 4 * 3
MAX_X, MAX_Y = 740, 493
MAX_FPS = 0
LEVEL_TWO_MUSIC_PATH = os.path.join(BASE_DIR, "../../Audio/LevelTwoBGM.mp3")
FADE_LEVEL = 100
FADE_CHANGE_PER_FRAME = 3
FADE_IN_CHANGE_PER_FRAME = 15
WATER_PATHS = [os.path.join(BASE_DIR, '../../Assets/Water/0.png'),
               os.path.join(BASE_DIR, '../../Assets/Water/1.png'),
               os.path.join(BASE_DIR, '../../Assets/Water/2.png'),
               os.path.join(BASE_DIR, '../../Assets/Water/3.png')]
PLAYER_PATHS = [os.path.join(BASE_DIR, '../../Assets/Players/Darnielle/walkLeft.png'),
                os.path.join(BASE_DIR, '../../Assets/Players/Darnielle/walkRight.png'),
                os.path.join(BASE_DIR, '../../Assets/Players/Darnielle/walkFront.png'),
                os.path.join(BASE_DIR, '../../Assets/Players/Darnielle/walkBack.png')]
POKEMON_PATHS = [os.path.join(BASE_DIR, '../../Assets/Pokemon/pokeL.png'),
                 os.path.join(BASE_DIR, '../../Assets/Pokemon/pokeR.png')]  # Assuming single image for simplicity
TREE_PATH = [os.path.join(BASE_DIR, '../../Assets/Background/Tree.png')]
LEAF_PATH = [os.path.join(BASE_DIR, '../../Assets/Background/Leaf.png')]
FURINA_PATHS = [os.path.join(BASE_DIR, '../../Assets/Players/Furina/WalkLeftFurina.png'),
                os.path.join(BASE_DIR, '../../Assets/Players/Furina/WalkRightFurina.png')]
FURINA_ROAD = [RIGHT, RIGHT, RIGHT, UP, RIGHT, UP, RIGHT, UP, RIGHT,
               RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT]

STAGES = {}
FURINA_SIZE = (48, 64)
FURINA_GO_SPEED = BLOCK_SIZE * 4
FURINA_PROD_TEXT = os.path.join(BASE_DIR, "LevelTwoWarpingWithoutFurina.txt")
FURINA_EVENT_PATH = os.path.join(BASE_DIR, "LevelTwoFurinaEvent.txt")
INTERACTABLE_BOUNDS = [BLOCK_SIZE, BLOCK_SIZE]

WATER_SPEED = 1
GAME_VOLUME = 0.3
ANIM_SPEED = 6
ANIM_DIST = 4
SWAY_SPEED = BLOCK_SIZE
SWAY_INTERVAL = 2
SWAY_LENGTH = BLOCK_SIZE
SWAY_DELAY = 15
FLOAT_SPEED = BLOCK_SIZE // 3
FLOAT_INTERVAL = 4
FLOAT_LENGTH = BLOCK_SIZE
DIST_FROM_PLAYER = BLOCK_SIZE * 15
POKEMON_CRY = os.path.join(BASE_DIR, "../../Audio/Poke.wav")
POKEMON_SIZE = (64, 64)
DELAY_AFTER_CLICK = 4
TEXT_BOX_POS = (65, MAX_Y - 140)
TEXT_BUTTON, VOLUME_BUTTON = 1, 0
TEXT_PATH = os.path.join(BASE_DIR, "LevelTwoText.txt")
TEXT_BOX_PATHS = [os.path.join(BASE_DIR, "../../Assets/UI/TextBox.png"),
                  os.path.join(BASE_DIR, "../../Assets/UI/TextBoxArrow.png")]
DELAY_AT_START = 55
WARP_PATH = os.path.join(BASE_DIR, "../../Assets/Background/Warp.png")
LOCATION = "lake"
MAX_ALPHA = 255
FINAL_DELAY = 5

RAIN_COLOR = (173, 216, 230)  # Light blue
RAIN_WIDTH = 3
RAIN_HEIGHT = 10
RAIN_COUNT = 100
RAIN_SPEED = 250

pygame.init()
# screen = pygame.display.set_mode((MAX_X, MAX_Y), flags=pygame.SCALED, vsync=1) # Andre
screen = pygame.display.set_mode((MAX_X, MAX_Y)) # Rhysmond
pygame.display.set_caption("Level 2")

pokemon_frames = {
    'icons': import_folder_dict(os.path.join(BASE_DIR, '../../Assets/Pokemon/icons')),
    'pokemon': monster_importer(4, 2, os.path.join(BASE_DIR, '../../Assets/Pokemon/pokemon')),
    'ui': import_folder_dict(os.path.join(BASE_DIR, '../../Assets/UI/ui'))
}

# fonts
def get_font_path(*parts):
    return os.path.join(BASE_DIR, '..', '..', 'Assets', 'Fonts', *parts)

# Load fonts using absolute paths
fonts = {
    'dialog': pygame.font.Font(get_font_path('PixeloidSans.ttf'), 12),
    'regular': pygame.font.Font(get_font_path('PixeloidSans.ttf'), 12),
    'small': pygame.font.Font(get_font_path('PixeloidSans.ttf'), 11),
    'bold': pygame.font.Font(get_font_path('dogicapixelbold.otf'), 13),
}

class RainDrop:
    def __init__(self, player):
        self.player = player
        self.x = self.player.x + random.randint(-MAX_X // 2, MAX_X // 2)
        self.y = self.player.y + random.randint(-MAX_Y // 2, MAX_Y // 2)
        self.length = random.randint(8, 12)
        self.speed = random.uniform(180, 250)

    def update_position(self, dt):
        self.y += self.speed * dt
        if self.y - self.player.y > MAX_Y // 2:
            return False
        return True

    def render(self, screen):
        screen_x = int(self.x - self.player.x + MAX_X // 2)
        screen_y = int(self.y - self.player.y + MAX_Y // 2)
        pygame.draw.line(screen, RAIN_COLOR, (screen_x, screen_y), (screen_x, screen_y + self.length), RAIN_WIDTH)


class Leaf(BGAsset):
    """Comet background assets"""
    default_color = (255, 0, 0)  # Red
    max_count = 8
    tick = 0
    tick_betw_leaves = SWAY_DELAY

    def __init__(self, player):
        super().__init__()
        self.player = player
        self.x = self.player.x + random.randint(-MAX_X // 2 - 20, MAX_X // 2 + 20)
        self.y = self.player.y - MAX_Y // 2 - 30
        self.ticker = 0
        self.dx = math.cos(self.ticker) * SWAY_LENGTH
        self.dy = SWAY_SPEED
        self.maxImages = len(Leaf.images)

    def update_position(self, dt):
        """Update leaf position with delta time (dt in seconds)"""
        # If leaf is out of view (past bottom of screen relative to player), remove it
        if abs(self.y - self.player.y) >= MAX_Y or abs(self.x - self.player.x) >= MAX_X:
            return False

        # Update leaf's local position in world space using delta time
        self.y += self.dy * dt
        self.x += self.dx * dt

        # Update animation timer and frame
        self.curr_img += dt * ANIM_SPEED

        # Update swaying motion with delta time
        self.ticker += SWAY_INTERVAL * dt
        self.dx = math.cos(self.ticker) * SWAY_LENGTH

        return True

    def render(self, screen):
        screen_x = self.x - self.player.x + MAX_X // 2
        screen_y = self.y - self.player.y + MAX_Y // 2
        screen.blit(self.images[int(self.curr_img) % self.maxImages], (screen_x, screen_y))

    @classmethod
    def create(cls, player, dt):
        """Create a new leaf if conditions are met, using delta time"""
        cls.tick += dt
        if cls.count < cls.max_count and cls.tick > cls.tick_betw_leaves:
            cls.count += 1
            cls.tick = 0
            return cls(player)
        return None

class LevelTwoVolumeButton(LevelOneVolumeButton):

    def first_toggle(self):
        if self.game.save.getMuted():
            pygame.mixer.music.set_volume(0 if self.playing else GAME_VOLUME)
            StoryTextBox.clickSound.set_volume(0 if self.playing else GAME_VOLUME)
            BaseWarp.warpSound.set_volume(0 if self.playing else GAME_VOLUME)
            Menu.open_sound.set_volume(0 if self.playing else GAME_VOLUME)
            Menu.click_sound.set_volume(0 if self.playing else GAME_VOLUME)
            Menu.select_sound.set_volume(0 if self.playing else GAME_VOLUME)
            self.game.poke.cry.set_volume(0 if self.playing else GAME_VOLUME)
            self.playing = not self.playing
            self.update_image()

    def toggle_volume(self):
        pygame.mixer.music.set_volume(0 if self.playing else GAME_VOLUME)
        StoryTextBox.clickSound.set_volume(0 if self.playing else GAME_VOLUME)
        BaseWarp.warpSound.set_volume(0 if self.playing else GAME_VOLUME)
        Menu.open_sound.set_volume(0 if self.playing else GAME_VOLUME)
        Menu.click_sound.set_volume(0 if self.playing else GAME_VOLUME)
        Menu.select_sound.set_volume(0 if self.playing else GAME_VOLUME)
        self.game.save.updateMuted()
        self.game.poke.cry.set_volume(0 if self.playing else GAME_VOLUME)
        self.playing = not self.playing
        self.update_image()

    def update_image(self):
        self.image_idx = 1 if not self.playing else 0

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
        if not AnimatedSprite.ini:
            AnimatedSprite.init_assets(paths)
            AnimatedSprite.ini = True
        super().__init__(pos, AnimatedSprite.assets[0], groups, z)
        self.currImage = 0

    @classmethod
    def init_assets(cls, paths):
        for path in paths:
            try:
                cls.assets.append(pygame.image.load(path))
            except FileNotFoundError:
                surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
                surface.fill((255, 255, 255))
                cls.assets.append(surface)
        cls.length = len(cls.assets)

    def update(self, dt, *args, **kwargs):
        self.currImage += WATER_SPEED * dt
        self.image = AnimatedSprite.assets[int(self.currImage) % AnimatedSprite.length]

class Warp(Sprite):

    def __init__(self, pos, stage, image, groups, game, z=1):
        super().__init__(pos, image, groups, z)
        self.game = game
        self.stage = stage
        self.hitbox = pygame.Rect(self.rect.x + self.rect.width // 4, self.rect.y + self.rect.height // 4, self.rect.width // 2, self.rect.height // 2)

    def warp(self):
        self.game.save.updateStage(self.stage.title())
        self.game.save.updatePos(LOCATION)
        SaveSystem.write(self.game.save)
        self.game.nextStage = True


class EventWarp(Warp):

    def __init__(self, pos, stage, image, groups, game, cond, z=1):
        super().__init__(pos, stage, image, groups, game, z)
        self.cond = cond
        self.eventDone = False


    def warp(self):
        if self.cond():
            self.game.save.updateStage(self.stage.title())
            self.game.save.updatePos(LOCATION)
            self.game.nextStage = True
            SaveSystem.write(self.game.save)
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

class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, groups, size, z=2):
        super().__init__(groups)
        self.z = z
        self.facing = DOWN
        self.currImage = 0
        self.x = pos[0]
        self.y = pos[1]
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.rect.center = pos
        self.hitbox = pygame.Rect(self.x + size[0] // 4, self.y + size[1] // 2, size[0] // 2, size[1] // 8 * 3)
        self.y_sort = self.rect.centery

    def input(self, dt):
        pass

    def move(self):
        pass

    def update(self, dt):
        self.input(dt)
        self.move()

    def collide(self):
        pass

class MC(Entity):
    ini = False
    assets = []

    def __init__(self, pos, paths, group, collidable, game, size, z=2):
        if not MC.ini:
            MC.init_assets(paths)
            MC.ini = True
        super().__init__(pos, group, size, z)
        self.game = game
        self.image = MC.assets[self.facing][self.currImage]
        self.moved = False
        self.collidable = collidable
        self.moving = False
        self.old_x = self.x
        self.old_y = self.y
        self.speed = PLAYER_SPEED
        self.blocked = False
        self.hitbox = pygame.Rect(self.x + size[0] * 15 // 32, self.y + size[1] * 15 // 32, size[0] // 8, size[1] // 8)
        #player Pokemon
        self.player_pokemon = {
            0: Pokemon('Charmadillo', 30),
            1: Pokemon('Friolera', 29),
            2: Pokemon('Plumette', 30),
            3: Pokemon('Ivieron', 29),
            4: Pokemon('Sparchu', 30),
            5: Pokemon('Cindrill', 29),
            6: Pokemon('Cindrill', 100)
        }

        if self.facing == LEFT:
            self.maxFrames = MC.leftFrames
        if self.facing == RIGHT:
            self.maxFrames = MC.rightFrames
        if self.facing == UP:
            self.maxFrames = MC.upFrames
        if self.facing == DOWN:
            self.maxFrames = MC.downFrames

    @classmethod
    def init_assets(cls, paths):
        for path in paths:
            try:
                surface = pygame.image.load(path)
            except FileNotFoundError:
                surface = pygame.Surface(PLAYER_SIZE)
                surface.fill((255, 255, 255))

            sheet_width, sheet_height = surface.get_size()
            columns = sheet_width // PLAYER_SIZE[0]
            rows = sheet_height // PLAYER_SIZE[1]

            frames = []
            for row in range(rows):
                for col in range(columns):
                    x = col * PLAYER_SIZE[0]
                    y = row * PLAYER_SIZE[1]
                    rect = pygame.Rect(x, y, PLAYER_SIZE[0], PLAYER_SIZE[1])
                    frame = surface.subsurface(rect)
                    frames.append(frame)

            cls.assets.append(frames)

        cls.upFrames = len(cls.assets[UP])
        cls.downFrames = len(cls.assets[DOWN])
        cls.leftFrames = len(cls.assets[LEFT])
        cls.rightFrames = len(cls.assets[RIGHT])

    def input(self, dt):
        # Store previous position
        if self.game.textComplete and not self.game.inEvent and not self.blocked:
            self.old_x, self.old_y = self.x, self.y
            keys = pygame.key.get_pressed()
            up = keys[pygame.K_UP] or keys[pygame.K_w]
            down = keys[pygame.K_DOWN] or keys[pygame.K_s]
            left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.speed = min(self.speed + 1, MAX_SPEED)
            else:
                self.speed = max(self.speed - 1, PLAYER_SPEED)

            if up and not down:
                self.y -= self.speed * dt * PLAYER_SPEED
                if (right or left) and not (left and right):
                    pass
                elif self.facing == UP:
                    self.currImage += ANIM_SPEED * dt
                else:
                    self.facing = UP
                    self.maxFrames = MC.upFrames
                    self.currImage = 0

            if down and not up:
                self.y += self.speed * dt * PLAYER_SPEED
                if (left or right) and not (left and right):
                    pass
                elif self.facing == DOWN:
                    self.currImage += ANIM_SPEED * dt
                else:
                    self.facing = DOWN
                    self.maxFrames = MC.downFrames
                    self.currImage = 0

            if left and not right:
                self.x -= self.speed * dt * PLAYER_SPEED
                if self.facing == LEFT:
                    self.currImage += ANIM_SPEED * dt
                else:
                    self.facing = LEFT
                    self.maxFrames = MC.leftFrames
                    self.currImage = 0

            if right and not left:
                self.x += self.speed * dt * PLAYER_SPEED
                if self.facing == RIGHT:
                    self.currImage += ANIM_SPEED * dt
                else:
                    self.facing = RIGHT
                    self.maxFrames = MC.rightFrames
                    self.currImage = 0
            if not left and not right and not up and not down:
                self.currImage = 0

    def move(self):

        # Update position
        self.rect.center = (self.x, self.y)
        self.hitbox.center = (self.x, self.y + PLAYER_SIZE[1] // 4)

        # Check for collisions
        self.collide()

        # Update sprite properties
        self.y_sort = self.rect.centery
        self.image = MC.assets[self.facing][int(self.currImage) % self.maxFrames]

    def collide(self):
        # Check for collisions with all collidable sprites
        for sprite in self.collidable:
            if sprite.hitbox.colliderect(self.hitbox):
                if isinstance(sprite, Warp):
                    sprite.warp()
                # Move back to previous position if collision occurs
                self.x, self.y = self.old_x, self.old_y
                self.rect.center = (self.x, self.y)
                self.hitbox.center = (self.x + PLAYER_SIZE[0] // 4, self.y + PLAYER_SIZE[1] // 4)
                break
    def toggleblock(self):
        self.blocked = not self.blocked


class Furina(Entity):

    ini = False
    assets = []

    def __init__(self, pos, paths, group, game, size, road, z=2):
        if not Furina.ini:
            Furina.init_assets(paths)
            Furina.ini = True
        super().__init__(pos, group, size, z)
        self.game = game
        self.facing = LEFT
        self.image = Furina.assets[self.facing][self.currImage]
        self.road = road
        self.currentStep = 0
        self.maxSteps = len(self.road)
        self.box = pygame.Rect(self.rect.x - INTERACTABLE_BOUNDS[0], self.rect.y - INTERACTABLE_BOUNDS[1], self.rect.width + 2 * INTERACTABLE_BOUNDS[0], self.rect.height + 2 * INTERACTABLE_BOUNDS[1])

        #GO event
        self.eventDone = False
        self.ticker = 0
        self.inEvent = False
        self.go = False

    @classmethod
    def init_assets(cls, paths):
        for path in paths:
            try:
                surface = pygame.image.load(path)
            except FileNotFoundError:
                surface = pygame.Surface(PLAYER_SIZE)
                surface.fill((255, 255, 255))

            sheet_width, sheet_height = surface.get_size()
            columns = sheet_width // FURINA_SIZE[0]
            rows = sheet_height // FURINA_SIZE[1]

            frames = []
            for row in range(rows):
                for col in range(columns):
                    x = col * FURINA_SIZE[0]
                    y = row * FURINA_SIZE[1]
                    rect = pygame.Rect(x, y, FURINA_SIZE[0], FURINA_SIZE[1])
                    frame = surface.subsurface(rect)
                    frames.append(frame)

            cls.assets.append(frames)

        cls.leftFrames = len(cls.assets[LEFT])
        cls.rightFrames = len(cls.assets[RIGHT])

    def move(self, dt):
        # Store previous position
        if self.go and self.currentStep < self.maxSteps:
            self.game.poke.bye = True
            down = self.road[int(self.currentStep)] == DOWN
            left = self.road[int(self.currentStep)] == LEFT
            right = self.road[int(self.currentStep)] == RIGHT
            up = self.road[int(self.currentStep)] == UP

            if left and not right:
                self.x -= dt * FURINA_GO_SPEED
                if self.facing == LEFT:
                    self.currImage += dt * ANIM_SPEED
                else:
                    self.facing = LEFT
                    self.currImage = 0

            elif right and not left:
                self.x += dt * FURINA_GO_SPEED
                if self.facing == RIGHT:
                    self.currImage += dt * ANIM_SPEED
                else:
                    self.facing = RIGHT
                    self.currImage = 0

            else:
                self.y = self.y + dt * FURINA_GO_SPEED if down else self.y - dt * FURINA_GO_SPEED
                self.currImage += dt * ANIM_SPEED

            self.currentStep += dt * ANIM_DIST

        elif self.go:
            self.game.inEvent = False
            self.game.met = True
            self.kill()
            self.game.poke.kill()
        else:
            pass

    def collide(self):
        keys = pygame.key.get_pressed()
        if self.box.colliderect(self.game.player.hitbox) and keys[pygame.K_SPACE] and not self.eventDone:
            self.eventDone = True
            self.inEvent = True
            self.game.inEvent = True
            self.makeEvent()

    def update(self, dt):
        # Update position
        self.rect.center = (self.x, self.y)
        self.hitbox.center = (self.x, self.y + PLAYER_SIZE[1] // 4)

        # Check for collisions
        if self.inEvent and self.game.textComplete:
            self.go = True

        # Update sprite properties
        self.move(dt)
        self.y_sort = self.rect.centery
        self.image = Furina.assets[self.facing][int(self.currImage) % Furina.leftFrames]

    def makeEvent(self):
        StoryTextBox.init__text(FURINA_EVENT_PATH)
        self.game.buttons[TEXT_BUTTON].reset()


class Poke(Entity):
    def __init__(self, pos, image_paths, group, size, game, z=4):
        super().__init__(pos, group, size, z)
        self.ran = False
        self.floatStage = 0
        self.inc = True
        self.game = game

        self.cry = pygame.mixer.Sound(POKEMON_CRY)
        self.cry.set_volume(GAME_VOLUME)

        self.player = game.player
        self.follow_distance = BLOCK_SIZE * 2

        # Load images
        self.images = []
        for path in image_paths:
            try:
                image = pygame.image.load(path)
            except FileNotFoundError:
                image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
                image.fill((255, 0, 0))  # Red as error indicator
            self.images.append(image)
        self.image = self.images[1 if self.player.x > self.rect.x + BLOCK_SIZE * 3 else 0]
        self.rect = self.image.get_rect(center=pos)

        # Movement constants (now in units per second)
        self.float_speed = FLOAT_SPEED # pixels per second
        self.float_length = FLOAT_LENGTH  # pixels
        self.float_interval = FLOAT_INTERVAL # radians per second
        self.follow_speed = 0.2 # proportion per second

        # Furina takes him away
        self.bye = False
        self.byecry = True

    def update(self, dt):
        # Update facing direction image
        self.image = self.images[1 if self.player.x > self.rect.x + BLOCK_SIZE * 3 else 0]

        if self.bye:
            if self.byecry:
                self.game.poke.cry.play()
                self.byecry = False
            self.player = self.game.furina

        if self.ran:
            # Follow player with some delay (framerate-independent)
            target_x = self.player.x
            target_y = self.player.y
            self.facing = self.player.facing

            # Calculate direction vector
            dx = target_x - self.x
            dy = target_y - self.y
            distance = max(BLOCK_SIZE, (dx**2 + dy**2)**0.5)

            # Normalize and scale by follow distance and delta time
            if distance > self.follow_distance:
                self.x += dx * self.follow_speed * dt * ANIM_SPEED
                self.y += dy * self.follow_speed * dt * ANIM_SPEED

            # Update facing direction
            if abs(dx) > abs(dy):
                self.facing = RIGHT if dx > 0 else LEFT
            else:
                self.facing = DOWN if dy > 0 else UP

        else:
            # Floating animation (framerate-independent)
            self.x += self.float_speed * dt * ANIM_SPEED
            self.y = self.player.y + self.float_length * math.sin(self.floatStage)
            self.floatStage += self.float_interval * dt

            # Check if we should start following
            if self.x >= self.player.x + BLOCK_SIZE * 1.5:
                self.ran = True
                self.cry.play()

        # Update position and sorting
        self.rect.center = (self.x, self.y)
        self.y_sort = self.rect.centery

class LevelTwo:

    def __init__(self, screen, start_pos, save):
        LevelTwo.tmx = load_pygame(TMX_PATH)
        self.start_pos = start_pos
        self.screen = screen
        self.save = save
        self.sprite_group = AllSprites()
        self.collide = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.buttons = []
        self.leaves = []
        self.alpha = 255
        self.rect = self.screen.get_rect()
        self.fadeInSurface = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)

        self.ticker = 0

        self.met = False
        self.textComplete = False
        self.boxFinished = False
        self.isClicked = False
        self.clickDelay = 0

        self.inEvent = False
        self.updateEvent = None

        self.nextStage = None
        self.stageDone = False
        self.finalDelay = 0

        self.raindrops = []

    def init_assets(self, start_pos):
        # Ground tiles
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Ground").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=1)

        # Water tiles
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Water").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            AnimatedSprite(pos, WATER_PATHS, groups=(self.sprite_group, self.collide), z=0)

        # Players
        for obj in LevelTwo.tmx.get_layer_by_name("Player"):
            if obj.properties["pos"] == start_pos:
                self.player = MC((obj.x, obj.y + 16), PLAYER_PATHS, self.sprite_group, self.collide, self, size=PLAYER_SIZE, z=3)

        # Grass tiles
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Grass").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=3)

        # Trees
        #tree_image = pygame.image.load(TREE_PATH[0])
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("LowerTrees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            tree = Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.collide), z=3)

        # Trees
        #tree_image = pygame.image.load(TREE_PATH[0])
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("UpperTrees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            tree = Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=3)

        # Trees
        #tree_image = pygame.image.load(TREE_PATH[0])
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Trunk").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            tree = Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=2)

        # Trees
        #tree_image = pygame.image.load(TREE_PATH[0])
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("FixTrees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            tree = Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=3)

        # Trees
        #tree_image = pygame.image.load(TREE_PATH[0])
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("TreesBelowBuildings").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            tree = Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=4)

        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Waterside").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=1)

        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Base").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=1)

        #tree_image = pygame.image.load(TREE_PATH[0])
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Buildings").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.collide), z=3)


        # Warps
        for obj in LevelTwo.tmx.get_layer_by_name("Warps"):
            FurinaWarp((obj.x, obj.y), obj.properties["pos"], image=pygame.image.load(WARP_PATH), groups=(self.sprite_group, self.collide), game=self, cond=lambda:self.met, z=2)

        self.poke = Poke((self.player.x - DIST_FROM_PLAYER, self.player.y), image_paths=POKEMON_PATHS, group=self.sprite_group, game=self, size=POKEMON_SIZE, z=4)

        #def __init__(self, pos, paths, group, game, road, z=2):

        for obj in LevelTwo.tmx.get_layer_by_name("Trainers"):
                if obj.name == "Furina":
                    self.furina = Furina((obj.x + FURINA_SIZE[0] // 4, obj.y + FURINA_SIZE[1] // 2), FURINA_PATHS, group=(self.sprite_group, self.collide, self.entities), game=self, size=FURINA_SIZE, road=FURINA_ROAD, z=3)

        # Pokemon menu
        self.menu = Menu(self.player.player_pokemon, fonts, pokemon_frames)
        self.menu_open = False

        pygame.mixer.music.load(LEVEL_TWO_MUSIC_PATH)
        pygame.mixer.music.set_volume(GAME_VOLUME)
        pygame.mixer.music.play(-1, 10, 5000)
        StoryTextBox.init__text(TEXT_PATH)
        StoryTextBox.init_images(TEXT_BOX_PATHS)
        LevelTwoVolumeButton.init_images(VOL_BUTTON_PATHS)
        Leaf.init_images(LEAF_PATH)
        self.buttons = [LevelTwoVolumeButton(MAX_X - 50, MAX_Y - 50, self)]
        self.buttons[VOLUME_BUTTON].first_toggle()


    def fade(self, dt):
        if not self.nextStage:
            self.fadeInSurface.fill((0, 0, 0, self.alpha))
            self.screen.blit(self.fadeInSurface, self.rect)
            if self.alpha > FADE_LEVEL:
                self.alpha = max(self.alpha - FADE_CHANGE_PER_FRAME * dt * ANIM_SPEED, FADE_LEVEL)

        else:
            self.fadeInSurface.fill((0, 0, 0, self.alpha))
            self.screen.blit(self.fadeInSurface, self.rect)
            if self.textComplete:
                self.alpha = min(self.alpha + FADE_IN_CHANGE_PER_FRAME * dt * ANIM_SPEED, MAX_ALPHA)

            if self.alpha >= MAX_ALPHA and self.finalDelay >= FINAL_DELAY:
                self.stageDone = True
            elif self.alpha >= MAX_ALPHA:
                self.finalDelay += dt * ANIM_SPEED

    def update_game_state(self, dt):
        #update player
        keys = pygame.key.get_pressed()
        for entity in self.entities:
            entity.collide()

        # Randomly create stars and comets
        Leaf.tick += dt * ANIM_SPEED
        if random.randint(0, 100) < 8:
            leaf = Leaf.create(self.player, dt)
            if leaf:
                self.leaves.append(leaf)

        # Create new raindrops
        if len(self.raindrops) < RAIN_COUNT:
            self.raindrops.append(RainDrop(self.player))

        # Update raindrop positions
        self.raindrops = [r for r in self.raindrops if r.update_position(dt)]

        if self.textComplete or self.ticker <= DELAY_AT_START:
            return

        if keys[pygame.K_SPACE] and not self.isClicked:
            self.buttons[TEXT_BUTTON].action()
            self.clickDelay = DELAY_AFTER_CLICK

        self.buttons[TEXT_BUTTON].updateString(dt)
        if self.isClicked:
            self.clickDelay -= dt * ANIM_SPEED
            if self.clickDelay <= 0:
                self.isClicked = False

    def redraw(self, dt):
        for raindrop in self.raindrops:
            raindrop.render(self.screen)

        # Draw buttons
        for i, button in enumerate(self.buttons):
            if i != TEXT_BUTTON or not self.textComplete:
                button.draw(self.screen)

        # Update and draw leaf
        self.leaves = [leaf for leaf in self.leaves if leaf.update(self.screen, dt)]

    def handle_events(self):

        """Handle all pygame events"""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            """Handle all pygame events"""
            # Update hover state for all buttons
            for button in self.buttons:
                if not self.textComplete or not isinstance(button, StoryTextBox):
                    button.check_hover(mouse_pos)

            # Handle button events
            for button in self.buttons:
                if not self.textComplete or not isinstance(button, StoryTextBox):
                    if button.handle_event(event):
                        break  # If a button was clicked, don't process other buttons

        if self.updateEvent:
            self.updateEvent()

    def input(self):
        keys = pygame.key.get_pressed()

        if self.textComplete and not self.inEvent and keys[pygame.K_RETURN] and not self.prev_keys[pygame.K_RETURN]:
            self.menu.open_sound.play()
            self.menu_open = not self.menu_open
            self.player.toggleblock()

        self.prev_keys = keys

    def run(self):
        self.init_assets(self.start_pos)
        self.clock = pygame.time.Clock()
        self.running = True

        while self.running and not self.stageDone:
            dt = self.clock.tick(MAX_FPS) / 1000.0  # Convert milliseconds to seconds
            if self.ticker < DELAY_AT_START:
                self.ticker = min(self.ticker + dt * ANIM_SPEED, DELAY_AT_START)
            elif self.ticker == DELAY_AT_START:
                self.ticker += dt
                self.buttons.append(StoryTextBox(TEXT_BOX_POS[0], TEXT_BOX_POS[1], self))

            if not self.nextStage:
                self.handle_events()
                self.update_game_state(dt)
                self.input()
                self.sprite_group.update(dt)

            self.screen.fill("black")
            self.sprite_group.draw(self.player.rect.center)
            self.redraw(dt)
            if self.menu_open: self.menu.update(dt)
            self.fade(dt)

            pygame.display.flip()

        if self.nextStage:
            return self.save.getStage()(self.screen, LOCATION, self.save)
        else:
            pygame.quit()
            sys.exit()


def checkExit(nextStage):
    if nextStage is not None:
        return nextStage.run()
    else:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    save = Save("test")
    save.updateStage("LevelTwo")
    save.updatePos(START_POS)
    SaveSystem.write(save)
    game = LevelTwo(screen, START_POS, save)
    nextStage = game.run()
    while True:
        nextStage = checkExit(nextStage)

