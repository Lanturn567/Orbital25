import pygame
import LevelOne
import Opening
import sys
from pytmx.util_pygame import load_pygame

from Opening import GAME_DELAY

TMX_PATH = "LevelTwo-TileMap.tmx"
START_POS = "begin"
BLOCK_SIZE = 32
PLAYER_SIZE = (32, 64)
MAX_X, MAX_Y = 740, 493
LEVEL_TWO_MUSIC_PATH = "./music/LevelTwoBGM.mp3"
FADE_LEVEL = 125
FADE_CHANGE_PER_FRAME = 6
WATER_PATHS = ["Water1.png", "Water2.png", "Water3.png"]
PLAYER_PATHS = ["./Player/walkFront.png", "./Player/walkLeft.png", "./Player/walkRight.png", "./Player/walkBack.png"]
GAME_VOLUME = 0.3
DOWN, LEFT, RIGHT, UP = 0, 1, 2, 3

#to remove
pygame.init()
screen = pygame.display.set_mode((MAX_X, MAX_Y))
pygame.display.set_caption("L2")

class AllSprites(pygame.sprite.LayeredUpdates):  # Changed from Group to LayeredUpdates
    def __init__(self):
        super().__init__()
        self.surf = pygame.display.get_surface()
        self.offsetX = 0
        self.offsetY = 0

    def draw(self, center):
        self.offsetX = -(center[0] - MAX_X // 2)
        self.offsetY = -(center[1] - MAX_Y // 2)

        bg_sprites = sorted([sprite for sprite in self if sprite.z == 0], key=lambda sprite:sprite.y_sort)
        water_sprites = sorted([sprite for sprite in self if sprite.z == 1], key=lambda sprite:sprite.y_sort)
        base_sprites = sorted([sprite for sprite in self if sprite.z == 2], key=lambda sprite:sprite.y_sort)
        tree_sprites = sorted([sprite for sprite in self if sprite.z == 3], key=lambda sprite:sprite.y_sort)

        for lis in (bg_sprites, water_sprites, base_sprites, tree_sprites):
            for sprite in lis:
                x, y = sprite.rect.topleft
                self.surf.blit(sprite.image, (x + self.offsetX, y + self.offsetY))

class MC(pygame.sprite.Sprite):
    assets = []
    ini = False

    def __init__(self, pos, paths, groups, z=2):
        if not MC.ini:
            MC.init_assets(paths)
            MC.ini = True
        super().__init__(groups)
        self.z = z
        self.facing = DOWN
        self.currImage = 0
        self.image = MC.assets[self.facing][self.currImage]
        self.rect = self.image.get_rect(center=pos)
        self.x = pos[0]
        self.y = pos[1]
        self.y_sort = self.rect.centery

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

            # Store frames in a list
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


    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= BLOCK_SIZE // 2
            if self.facing == UP:
                self.currImage = (self.currImage + 1) % MC.upFrames
            else:
                self.facing = UP
                self.currImage = 0

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += BLOCK_SIZE // 2
            if self.facing == DOWN:
                self.currImage = (self.currImage + 1) % MC.downFrames
            else:
                self.facing = DOWN
                self.currImage = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= BLOCK_SIZE // 2
            if self.facing == LEFT:
                self.currImage = (self.currImage + 1) % MC.leftFrames
            else:
                self.facing = LEFT
                self.currImage = 0

        if keys[pygame.K_RIGHT]or keys[pygame.K_d]:
            self.x += BLOCK_SIZE // 2
            if self.facing == RIGHT:
                self.currImage = (self.currImage + 1) % MC.rightFrames
            else:
                self.facing = RIGHT
                self.currImage = 0


    def move(self):
        self.rect.center = (self.x, self.y)
        self.y_sort = self.rect.centery
        self.image = MC.assets[self.facing][self.currImage]

    def update(self):
        self.input()
        self.move()

class Sprite(pygame.sprite.Sprite):

    def __init__(self, pos, image, groups, z=0):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z  # Add layer attribute
        self.y_sort = self.rect.centery - BLOCK_SIZE // 2

class AnimatedSprite(Sprite):
    assets = []
    ini = False
    length = 0

    def __init__(self, pos, paths, groups, z=0):
        if not AnimatedSprite.ini:
            AnimatedSprite.init__assets(paths)
            AnimatedSprite.ini = True
        super().__init__(pos, AnimatedSprite.assets[0], groups, z)
        self.currImage = 0

    @classmethod
    def init__assets(cls, paths):
        for path in paths:
            try:
                AnimatedSprite.assets.append(pygame.image.load(path))
            except FileNotFoundError:
                surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
                surface.fill((255, 255, 255))
                AnimatedSprite.assets.append(surface)
        cls.length = len(cls.assets)

    def update(self, *args, **kwargs):
        self.currImage = (self.currImage + 1) % AnimatedSprite.length
        self.image = AnimatedSprite.assets[self.currImage]



class LevelTwo:
    tmx = load_pygame(TMX_PATH)

    def __init__(self, screen, start_pos):
        self.start_pos = start_pos
        self.screen = screen
        self.sprite_group = AllSprites()
        self.alpha = 255
        self.rect = self.screen.get_rect()
        self.fadeInSurface = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)

    def init_assets(self, start_pos):
        # Ground tiles (lowest layer)
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Ground").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=0)

        # Water tiles (above ground)
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Water").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            AnimatedSprite(pos, WATER_PATHS, groups=self.sprite_group, z=1)


        # Player (middle layer, will be adjusted in update)
        for obj in LevelTwo.tmx.get_layer_by_name("Players"):
            if obj.properties["pos"] == start_pos:
                self.player = MC((obj.x, obj.y), PLAYER_PATHS, self.sprite_group, z=2)

        # Grass tiles - need special handling for player overlap
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Grass").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            # We'll set the layer dynamically based on player position
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=2)

        # Trees (top layer)
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Trees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=3)


    def fade(self):
        self.fadeInSurface.fill((0, 0, 0, max(self.alpha, FADE_LEVEL)))
        self.screen.blit(self.fadeInSurface, self.rect)
        if self.alpha > FADE_LEVEL:
            self.alpha -= FADE_CHANGE_PER_FRAME

    def run(self):
        self.init_assets(self.start_pos)
        pygame.mixer.music.load(LEVEL_TWO_MUSIC_PATH)
        pygame.mixer.music.set_volume(GAME_VOLUME)
        pygame.mixer.music.play(-1, 10, 5000)


        while True:
            pygame.time.delay(GAME_DELAY)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill("black")
            self.sprite_group.update()
            self.sprite_group.draw(self.player.rect.center)
            self.fade()
            pygame.display.flip()

if __name__ == "__main__":
    game = LevelTwo(screen, START_POS)
    game.run()