import pygame
import LevelOne
import Opening
import sys
from pytmx.util_pygame import load_pygame

from Opening import GAME_DELAY

TMX_PATH = "LevelTwo-TileMap.tmx"
BLOCK_SIZE = 32
PLAYER_SIZE = (32, 64)
MAX_X, MAX_Y = 740, 493
LEVEL_TWO_MUSIC_PATH = "./music/LevelOneIntro.mp3"
FADE_LEVEL = 125
FADE_CHANGE_PER_FRAME = 6

#to remove
pygame.init()
screen = pygame.display.set_mode((MAX_X, MAX_Y))
pygame.display.set_caption("L2")

class AllSprites(pygame.sprite.Group):

    def __init__(self):
        super().__init__()
        self.surf = pygame.display.get_surface()
        self.offsetX = 0
        self.offsetY = 0

    def draw(self, center):
        self.offsetX = -(center[0] - MAX_X // 2)
        self.offsetY = -(center[1] - MAX_Y // 2)

        for sprite in self:
            x, y = sprite.rect.topleft
            self.surf.blit(sprite.image, (x + self.offsetX, y + self.offsetY))

class MC(pygame.sprite.Sprite):

    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((PLAYER_SIZE[0], PLAYER_SIZE[1]))
        self.image.fill('red')
        self.rect = self.image.get_rect(center=pos)
        self.x = pos[0]
        self.y = pos[1]


    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= BLOCK_SIZE // 2
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += BLOCK_SIZE // 2
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= BLOCK_SIZE // 2
        if keys[pygame.K_RIGHT]or keys[pygame.K_d]:
            self.x += BLOCK_SIZE // 2

    def move(self):
        self.rect.center = (self.x, self.y)

    def update(self):
        self.input()
        self.move()

class Tile(pygame.sprite.Sprite):

    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)

class LevelTwo:
    tmx = load_pygame(TMX_PATH)

    def __init__(self, screen):
        self.screen = screen
        self.sprite_group = AllSprites()
        self.alpha = 255
        self.rect = self.screen.get_rect()
        self.fadeInSurface = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)

    def init_assets(self, start_pos):
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Ground").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Tile(pos=pos, surf=surf, groups=self.sprite_group)

        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Grass").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Tile(pos=pos, surf=surf, groups=self.sprite_group)

        for obj in LevelTwo.tmx.get_layer_by_name("Objects"):
            if obj.properties["pos"] == start_pos:
                self.player = MC((obj.x, obj.y), self.sprite_group)

    def fade(self):
        self.fadeInSurface.fill((0, 0, 0, max(self.alpha, FADE_LEVEL)))
        self.screen.blit(self.fadeInSurface, self.rect)
        if self.alpha > FADE_LEVEL:
            self.alpha -= FADE_CHANGE_PER_FRAME

    def run(self):
        self.init_assets("begin")
        pygame.mixer.music.load(LEVEL_TWO_MUSIC_PATH)
        pygame.mixer.music.play(-1, 4)


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
    game = LevelTwo(screen)
    game.run()