import pygame
import sys
import math
import random
import os
import copy
from Code.support import *
from pytmx.util_pygame import load_pygame
from Code.LevelTwoStage.StoryTextBox import StoryTextBox
from Code.LevelOneStage.LevelOne import LevelOneVolumeButton, VOL_BUTTON_PATHS
from Code.Opening.Opening import BGAsset
from Code.sprites import *
from Code.Save import *
from Code.entities import *
from Code.support import *
from Code.Battle import Battle


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
BATTLE_MUSIC_PATH = os.path.join(BASE_DIR, "../../Audio/Battle/battle_song.mp3")
POKEBALL_PATH = [os.path.join(BASE_DIR, '../../Assets/backgrounds/pokeball.png')]
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

# pokemon frames
pokemon_frames = {
    'icons': import_folder_dict(os.path.join(BASE_DIR, '../../Assets/Pokemon/icons')),
    'pokemon': monster_importer(4, 2, os.path.join(BASE_DIR, '../../Assets/Pokemon/pokemon')),
    'ui': import_folder_dict(os.path.join(BASE_DIR, '../../Assets/UI/ui')),
    'attacks': attack_importer(os.path.join(BASE_DIR, '../../Assets/attacks'))
}
pokemon_frames['outlines'] = outline_creator(pokemon_frames['pokemon'], 4)

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

#bg frames
bg_frames = import_folder_dict(os.path.join(BASE_DIR, '../../Assets/backgrounds'))

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
            Battle.select_sound.set_volume(0 if self.playing else GAME_VOLUME)
            Battle.toggle_sound.set_volume(0 if self.playing else GAME_VOLUME)
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
        Battle.select_sound.set_volume(0 if self.playing else GAME_VOLUME)
        Battle.toggle_sound.set_volume(0 if self.playing else GAME_VOLUME)
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
            del self.game.player.player_pokemon[0]
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
        self.encounter = pygame.sprite.Group()
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
        self.monsters = [
            {0: Pokemon('Atrox', 1)},
            {0: Pokemon('Cleaf', 3)},
            {0: Pokemon('Jacana', 4)}
        ]

        self.encounter_timer = Timer(2000, func=self.pokemon_encounter)

        # transition / tint
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.transition_target = None
        self.tint_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.tint_mode = 'untint'
        self.tint_progress = 0
        self.tint_direction = -1
        self.tint_speed = 600
        self.tint_type = 'fade'  # 'fade' or 'flash'
        self.flash_count = 0
        self.flash_total = 3  # 3 flashes = 6 transitions (in+out x3)
        self.flash_state = 'in'  # current phase of a flash

        self.transition_music_path = BATTLE_MUSIC_PATH
        self.transition_music_playing = False
        self.bg_music_muted = False

        # Add pokeball image loading
        self.pokeball_image = pygame.image.load(POKEBALL_PATH[0]).convert_alpha()
        self.pokeball_rect = self.pokeball_image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.pokeball_alpha = 0
        self.show_pokeball = False

        # Add pokeball fade speed
        self.pokeball_fade_speed = 20000

        # Pokeball animation properties
        self.pokeball_scale = 1.0
        self.pokeball_target_scale = 5.0
        self.pokeball_growth_duration = 700
        self.pokeball_growth_timer = 0
        self.pokeball_growing = False
        self.pokeball_rotation = 0  # Current rotation angle (degrees)
        self.pokeball_target_rotation = 360  # Complete 1 full rotation

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
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.encounter), z=3)

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

        # Battle
        self.battle = None

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

    def check_pokemon(self):
        if [sprite for sprite in self.encounter if
            sprite.rect.colliderect(self.player.hitbox)] and not self.battle and self.player.moving:
            if not self.encounter_timer.active:
                self.encounter_timer.activate()

    def pokemon_encounter(self):
        print('lol')
        if [sprite for sprite in self.encounter if
            sprite.rect.colliderect(self.player.hitbox)] and not self.battle and self.player.moving and not self.player.has_no_pokemon():
            selected_monsters = random.choice(self.monsters)
            self.start_battle(copy.deepcopy(selected_monsters), None)

    def end_battle(self):
        self.encounter_timer.deactivate()
        self.transition_target = 'level'  # Signal we're returning to overworld
        self.tint_mode = 'tint'  # Start fading to black
        self.tint_type = 'fade'
        self.tint_progress = 0  # Reset progress

        # Reset pokeball state
        self.show_pokeball = False
        self.pokeball_alpha = 0

        # Reset music
        if self.transition_music_playing:
            pygame.mixer.music.load(LEVEL_TWO_MUSIC_PATH)
            volume = 0 if self.save.getMuted() else GAME_VOLUME
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
            self.transition_music_playing = False

        self.bg_music_muted = False
        self.player.blocked = True  # Keep player blocked during transition

    def start_battle(self, monsters, trainer):
        if self.battle is None:
            self.transition_target = Battle(
                player_pokemon=self.player.player_pokemon,
                opponent_pokemon=monsters,
                pokemon_frames=pokemon_frames,
                bg_surf=bg_frames['forest'],
                fonts=fonts,
                trainer=trainer,
                game=self
            )
            self.tint_mode = 'tint'
            self.tint_type = 'flash'
            self.flash_count = 0
            self.flash_total = 3
            self.flash_state = 'in'
            self.tint_progress = 0
            self.chain_fade_after_flash = True
            self.show_pokeball = False  # Start with pokeball hidden

            # Music: mute bg and play battle music
            if not self.bg_music_muted:
                pygame.mixer.music.set_volume(0)
                self.bg_music_muted = True

            if not self.transition_music_playing:
                pygame.mixer.music.load(self.transition_music_path)
                volume = 0 if self.save.getMuted() else GAME_VOLUME * 0.3
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1)
                self.transition_music_playing = True

            # block player
            self.player.blocked = True

    def tint_screen(self, dt):
        if self.tint_type == 'fade':
            if self.tint_mode == 'untint':
                self.tint_progress -= self.tint_speed * dt
                if self.show_pokeball:
                    self.pokeball_alpha -= self.pokeball_fade_speed * dt
                    self.pokeball_alpha = max(0, self.pokeball_alpha)

                # When fade out completes
                if self.tint_progress <= 0:
                    if self.transition_target == 'level':
                        # Clear battle and return to overworld
                        self.battle = None
                        self.player.blocked = False  # Now unblock player
                        self.transition_target = None
                    elif isinstance(self.transition_target, Battle):
                        # Transition to new battle
                        self.battle = self.transition_target
                        self.transition_target = None

            elif self.tint_mode == 'tint':
                self.tint_progress += self.tint_speed * dt
                if self.show_pokeball:
                    self.pokeball_alpha += self.pokeball_fade_speed * dt
                    self.pokeball_alpha = min(255, self.pokeball_alpha)

                # When screen is fully black
                if self.tint_progress >= 255:
                    if self.transition_target == 'level':
                        # SWITCH TO OVERWORLD HERE
                        self.battle = None
                        self.transition_target = None
                        self.tint_mode = 'untint'  # begin fade-in
                        self.player.blocked = False
                        self.show_pokeball = False

                    elif isinstance(self.transition_target, Battle):
                        # SWITCH TO BATTLE HERE
                        self.battle = self.transition_target
                        self.transition_target = None
                        self.tint_mode = 'untint'  # begin fade-in
                        self.show_pokeball = False

        elif self.tint_type == 'flash':
            speed = self.tint_speed * dt * 3

            if self.flash_state == 'in':
                self.tint_progress += speed
                if self.tint_progress >= 255:
                    self.tint_progress = 255
                    self.flash_state = 'out'
            elif self.flash_state == 'out':
                self.tint_progress -= speed
                if self.tint_progress <= 0:
                    self.tint_progress = 0
                    self.flash_count += 1
                    if self.flash_count >= self.flash_total:
                        # Transition to pokeball sequence
                        self.tint_type = 'pokeball'
                        self.tint_mode = 'tint'
                        self.tint_progress = 0
                        self.show_pokeball = True
                    else:
                        self.flash_state = 'in'


        elif self.tint_type == 'pokeball':
            if self.tint_mode == 'tint':
                # Step 1: Fade-in pokeball
                self.pokeball_alpha += self.pokeball_fade_speed * dt
                if self.pokeball_alpha >= 255:
                    self.pokeball_alpha = 255
                    self.tint_mode = 'grow_pokeball'
                    self.pokeball_growing = True
                    self.pokeball_growth_timer = 0
                    self.pokeball_scale = 1.0  # Start at normal size
                    self.pokeball_rotation = 0  # Reset rotation

            elif self.tint_mode == 'grow_pokeball':
                # Step 2: Grow and spin pokeball over 2 seconds
                self.pokeball_growth_timer += dt * 1000  # Convert to milliseconds
                # Calculate growth progress (0 to 1)
                growth_progress = min(1.0, self.pokeball_growth_timer / self.pokeball_growth_duration)
                # Ease-out scaling for smoother animation
                eased_progress = 1 - (1 - growth_progress) ** 2
                self.pokeball_scale = 1 + (self.pokeball_target_scale - 1) * eased_progress
                # Update rotation (complete 360 degrees over the growth duration)
                self.pokeball_rotation = growth_progress * self.pokeball_target_rotation
                # When growth completes
                if growth_progress >= 1.0:
                    self.tint_mode = 'fadeout_pokeball'
                    self.tint_progress = 0  # Reset tint for fade-to-black
                    self.pokeball_growing = False

            elif self.tint_mode == 'fadeout_pokeball':
                # Step 3: Fade screen to black over pokeball
                self.tint_progress += self.tint_speed * dt
                if self.tint_progress >= 255:
                    self.tint_progress = 255
                    self.tint_mode = 'hold_black'
                    self.pokeball_alpha = 0
                    self.black_hold_timer = 0
                    self.pokeball_scale = 1.0  # Reset scale

            elif self.tint_mode == 'hold_black':
                self.black_hold_timer += dt
                if self.black_hold_timer >= 1:
                    # Transition into battle BEFORE fade-in
                    if isinstance(self.transition_target, Battle):
                        self.battle = self.transition_target
                        self.transition_target = None
                    self.tint_type = 'fade'
                    self.tint_mode = 'untint'
                    self.tint_progress = 255  # Start fade-in from black

        # Apply the tints and overlays
        self.tint_progress = max(0, min(self.tint_progress, 255))
        self.tint_surf.set_alpha(self.tint_progress)
        self.display_surface.blit(self.tint_surf, (0, 0))

        # Modified pokeball drawing
        if self.show_pokeball and self.pokeball_alpha > 0:
            # Create scaled pokeball surface
            scaled_width = int(self.pokeball_image.get_width() * self.pokeball_scale)
            scaled_height = int(self.pokeball_image.get_height() * self.pokeball_scale)

            # Rotate the original image first (better quality than rotating scaled image)
            rotated_pokeball = pygame.transform.rotate(self.pokeball_image, -self.pokeball_rotation)

            # Then scale the rotated image
            scaled_pokeball = pygame.transform.scale(
                rotated_pokeball,
                (scaled_width, scaled_height)
            )

            # Center the scaled and rotated pokeball
            pokeball_rect = scaled_pokeball.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

            # Apply alpha and draw
            scaled_pokeball.set_alpha(self.pokeball_alpha)
            self.display_surface.blit(scaled_pokeball, pokeball_rect)

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
                self.encounter_timer.update()
                self.check_pokemon()
                self.input()
                self.sprite_group.update(dt)

            self.screen.fill("black")
            self.sprite_group.draw(self.player.rect.center)
            self.redraw(dt)
            if self.menu_open: self.menu.update(dt)
            if self.battle: self.battle.update(dt)

            self.buttons[VOLUME_BUTTON].draw(self.screen)
            self.fade(dt)
            self.tint_screen(dt)

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

