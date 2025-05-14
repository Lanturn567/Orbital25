import pygame
import sys
import math
from Home import Home
from Mountain import Mountain
from pytmx.util_pygame import load_pygame
from StoryTextBox import StoryTextBox
from LevelOne import LevelOneVolumeButton, ALPHA_CHANGE

# Constants
TMX_PATH = "LevelTwo-TileMap.tmx"
START_POS = "begin"
BLOCK_SIZE = 32
PLAYER_SIZE = (32, 64)
PLAYER_SPEED = BLOCK_SIZE // 3
MAX_SPEED = BLOCK_SIZE * 7 // 10
MAX_X, MAX_Y = 740, 493
LEVEL_TWO_MUSIC_PATH = "./music/LevelTwoBGM.mp3"
FADE_LEVEL = 100
FADE_CHANGE_PER_FRAME = 6
WATER_PATHS = ["./Assets/Water1.png", "./Assets/Water2.png", "./Assets/Water3.png"]
PLAYER_PATHS = ["./Player/walkFront.png", "./Player/walkLeft.png", "./Player/walkRight.png", "./Player/walkBack.png"]
POKEMON_PATHS = ["./Assets/poke.png"]  # Assuming single image for simplicity
GAME_VOLUME = 0.3
GAME_DELAY = 100
DOWN, LEFT, RIGHT, UP = 0, 1, 2, 3
FLOAT_SPEED = BLOCK_SIZE // 3
FLOAT_INTERVAL = 0.4
FLOAT_LENGTH = BLOCK_SIZE
DIST_FROM_PLAYER = BLOCK_SIZE * 15
POKEMON_CRY = "./music/Poke.wav"
DELAY_AFTER_CLICK = 3
TEXT_BOX_POS = (65, MAX_Y - 140)
TEXT_BUTTON, VOLUME_BUTTON = 0, 1
TEXT_PATH = "LevelTwoText.txt"
TEXT_BOX_PATHS = ["./UI/TextBox.png", "./UI/TextBoxArrow.png"]
DELAY_AT_START = 55
WARP_PATH = "./Assets/Warp.png"
LOCATION = "lake"
STAGES = {"home" : lambda screen: Home(screen, LOCATION),
          "mountain" : lambda screen: Mountain(screen, LOCATION)}
MAX_ALPHA = 255
FINAL_DELAY = 5


# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((MAX_X, MAX_Y))
pygame.display.set_caption("Level 2")


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
        poke_sprites = sorted([sprite for sprite in self if sprite.z == 4], key=lambda sprite: sprite.y_sort)
        tree_sprites = sorted([sprite for sprite in self if sprite.z == 3], key=lambda sprite: sprite.y_sort)

        for lis in (bg_sprites, water_sprites, base_sprites, tree_sprites, poke_sprites):
            for sprite in lis:
                x, y = sprite.rect.topleft
                self.surf.blit(sprite.image, (x + self.offsetX, y + self.offsetY))


class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, groups, z=2):
        super().__init__(groups)
        self.z = z
        self.facing = DOWN
        self.currImage = 0
        self.x = pos[0]
        self.y = pos[1]
        self.rect = pygame.Rect(0, 0, PLAYER_SIZE[0], PLAYER_SIZE[1])
        self.rect.center = pos
        self.hitbox = pygame.Rect(self.x + PLAYER_SIZE[0] // 4, self.y + PLAYER_SIZE[1] // 4, PLAYER_SIZE[0] // 2, PLAYER_SIZE[1] // 2)
        self.y_sort = self.rect.centery

    def input(self):
        pass

    def move(self):
        pass

    def update(self):
        self.input()
        self.move()


class MC(Entity):
    ini = False
    assets = []

    def __init__(self, pos, paths, group, collidable, game, z=2):
        if not MC.ini:
            MC.init_assets(paths)
            MC.ini = True
        super().__init__(pos, group, z)
        self.game = game
        self.image = MC.assets[self.facing][self.currImage]
        self.moved = False
        self.collidable = collidable
        self.moving = False
        self.old_x = self.x
        self.old_y = self.y
        self.speed = PLAYER_SPEED

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

    def input(self):
        # Store previous position
        if self.game.poke.ran and self.game.textComplete:
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
                self.y -= self.speed
                if (right or left) and not (left and right):
                    pass
                elif self.facing == UP:
                    self.currImage = (self.currImage + 1) % MC.upFrames
                else:
                    self.facing = UP
                    self.currImage = 0

            if down and not up:
                self.y += self.speed
                if (left or right) and not (left and right):
                    pass
                elif self.facing == DOWN:
                    self.currImage = (self.currImage + 1) % MC.downFrames
                else:
                    self.facing = DOWN
                    self.currImage = 0

            if left and not right:
                self.x -= self.speed
                if self.facing == LEFT:
                    self.currImage = (self.currImage + 1) % MC.leftFrames
                else:
                    self.facing = LEFT
                    self.currImage = 0

            if right and not left:
                self.x += self.speed
                if self.facing == RIGHT:
                    self.currImage = (self.currImage + 1) % MC.rightFrames
                else:
                    self.facing = RIGHT
                    self.currImage = 0

    def move(self):

        # Update position
        self.rect.center = (self.x, self.y)
        self.hitbox.center = (self.x, self.y + PLAYER_SIZE[1] // 4)

        # Check for collisions
        self.collide()

        # Update sprite properties
        self.y_sort = self.rect.centery
        self.image = MC.assets[self.facing][self.currImage]

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


class Poke(Entity):
    def __init__(self, pos, image_path, group, player, z=4):
        super().__init__(pos, group, z)
        self.ran = False
        self.floatStage = 0
        self.inc = True

        self.cry = pygame.mixer.Sound(POKEMON_CRY)
        self.cry.set_volume(GAME_VOLUME)

        self.player = player
        self.follow_distance = BLOCK_SIZE * 2
        try:
            self.image = pygame.image.load(image_path)
        except FileNotFoundError:
            self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
            self.image.fill((255, 0, 0))  # Red as error indicator
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        if self.ran:
            # Follow player with some delay
            target_x = self.player.x
            target_y = self.player.y
            self.facing = self.player.facing

            # Calculate direction vector
            dx = target_x - self.x
            dy = target_y - self.y
            distance = max(32, (dx**2 + dy**2)**0.5)

            # Normalize and scale by follow distance
            if distance > self.follow_distance:
                self.x += dx * 0.15
                self.y += dy * 0.15

            # Update facing direction
            if abs(dx) > abs(dy):
                self.facing = RIGHT if dx > 0 else LEFT
            else:
                self.facing = DOWN if dy > 0 else UP

            self.rect.center = (self.x, self.y)
            self.y_sort = self.rect.centery

        else:
            self.x += FLOAT_SPEED
            self.y = self.player.y + FLOAT_LENGTH * math.sin(self.floatStage)
            self.rect.center = (self.x, self.y)
            self.floatStage += FLOAT_INTERVAL

            if self.x >= self.player.x + BLOCK_SIZE * 1.5:
                    self.ran = True
                    self.cry.play()


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

    def update(self, *args, **kwargs):
        self.currImage = (self.currImage + 1) % AnimatedSprite.length
        self.image = AnimatedSprite.assets[self.currImage]

class Warp(Sprite):

    def __init__(self, pos, stage, image, groups, game, z=2):
        super().__init__(pos, image, groups, z=2)
        self.game = game
        self.stage = STAGES.get(stage)(game.screen)
        self.hitbox = pygame.Rect(self.rect.x + self.rect.width // 4, self.rect.y + self.rect.height // 4, self.rect.width // 2, self.rect.height // 2)


    def warp(self):
        self.game.nextStage = self.stage

class LevelTwo:
    tmx = load_pygame(TMX_PATH)

    def __init__(self, screen, start_pos):
        self.start_pos = start_pos
        self.screen = screen
        self.sprite_group = AllSprites()
        self.collide = pygame.sprite.Group()
        self.alpha = 255
        self.rect = self.screen.get_rect()
        self.fadeInSurface = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)

        self.ticker = 0

        self.textComplete = False
        self.boxFinished = False
        self.isClicked = False
        self.clickDelay = 0

        self.nextStage = None
        self.stageDone = False
        self.finalDelay = 0


    def init_assets(self, start_pos):
        # Ground tiles
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Ground").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=0)

        # Water tiles
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Water").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            AnimatedSprite(pos, WATER_PATHS, groups=(self.sprite_group, self.collide), z=1)

        # Player
        for obj in LevelTwo.tmx.get_layer_by_name("Players"):
            if obj.properties["pos"] == start_pos:
                self.player = MC((obj.x + 16, obj.y), PLAYER_PATHS, self.sprite_group, self.collide, self, z=2)

        # Grass tiles
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Grass").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=2)

        # Trees
        for x, y, surf in LevelTwo.tmx.get_layer_by_name("Trees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.collide), z=2)

        # Warps
        for obj in LevelTwo.tmx.get_layer_by_name("Warps"):
            Warp((obj.x, obj.y), obj.properties["pos"], image=pygame.image.load(WARP_PATH), groups=(self.sprite_group, self.collide), game=self, z=2)

        self.poke = Poke((self.player.x - DIST_FROM_PLAYER, self.player.y), image_path=POKEMON_PATHS[0], group=self.sprite_group, player=self.player, z=4)

    def fade(self):
        if not self.nextStage:
            self.fadeInSurface.fill((0, 0, 0, max(self.alpha, FADE_LEVEL)))
            self.screen.blit(self.fadeInSurface, self.rect)
            if self.alpha > FADE_LEVEL:
                self.alpha -= FADE_CHANGE_PER_FRAME

        else:
            self.fadeInSurface.fill((0, 0, 0, min(MAX_ALPHA, self.alpha)))
            self.screen.blit(self.fadeInSurface, self.rect)
            if self.textComplete:
                self.alpha += FADE_CHANGE_PER_FRAME

            if self.alpha >= MAX_ALPHA and self.finalDelay >= FINAL_DELAY:
                self.stageDone = True
            elif self.alpha >= MAX_ALPHA:
                self.finalDelay += 1

    def update_game_state(self):
        #update player
        if self.textComplete or self.ticker <= DELAY_AT_START:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not self.isClicked:
            self.buttons[TEXT_BUTTON].action()


        self.buttons[TEXT_BUTTON].updateString()
        if self.isClicked:
            self.clickDelay = (self.clickDelay + 1) % DELAY_AFTER_CLICK
            if self.clickDelay == 0:
                self.isClicked = False

    def redraw(self):
        # Draw buttons
        if self.ticker > DELAY_AT_START:
            for i, button in enumerate(self.buttons):
                if i != TEXT_BUTTON or not self.textComplete:
                    button.draw(self.screen)

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

    def run(self):
        self.init_assets(self.start_pos)
        pygame.mixer.music.load(LEVEL_TWO_MUSIC_PATH)
        pygame.mixer.music.set_volume(GAME_VOLUME)
        pygame.mixer.music.play(-1, 10, 5000)
        StoryTextBox.init__text(TEXT_PATH)
        StoryTextBox.init_images(TEXT_BOX_PATHS)
        self.buttons = [StoryTextBox(TEXT_BOX_POS[0], TEXT_BOX_POS[1], self)]


        clock = pygame.time.Clock()
        self.running = True

        while self.running and not self.stageDone:

            if self.ticker < DELAY_AT_START:
                self.ticker += 1
            elif self.ticker == DELAY_AT_START:
                self.ticker += 1
                self.buttons = [StoryTextBox(TEXT_BOX_POS[0], TEXT_BOX_POS[1], self)]
            pygame.time.delay(GAME_DELAY)

            if not self.nextStage:
                self.handle_events()
                self.update_game_state()
                self.screen.fill("black")
                self.sprite_group.update()
                self.sprite_group.draw(self.player.rect.center)
                self.redraw()
            self.fade()
            pygame.display.flip()


        if self.nextStage:
            return self.nextStage
        else:
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    game = LevelTwo(screen, START_POS)
    next = game.run()
    next.run()

