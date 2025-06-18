import pygame
import sys
import math
import random
import os
from Code.sprites import *
from Code.support import *
from pytmx.util_pygame import load_pygame
from Code.LevelTwoStage.StoryTextBox import StoryTextBox
from Code.LevelOneStage.LevelOne import LevelOneVolumeButton, VOL_BUTTON_PATHS
from Code.Opening.Opening import BGAsset
from Code.Menu import *
from Code.Entities.Pokemon import *

# Constants
TMX_PATH = "../../../Data/TilemapsPNG/LevelTwo-TileMap.tmx"
START_POS = "begin"
DOWN, LEFT, RIGHT, UP = 2, 0, 1, 3
BLOCK_SIZE = 32
ASSET_SIZE = 32
PLAYER_SIZE = (32, 64)
PLAYER_SPEED = BLOCK_SIZE // 2
MAX_SPEED = BLOCK_SIZE // 4 * 3
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
POKEMON_CRY = os.path.join(BASE_DIR, '../Audio/Poke.wav')
POKEMON_SIZE = (64, 64)
DELAY_AFTER_CLICK = 4
TEXT_BOX_POS = (65, MAX_Y - 140)
TEXT_BUTTON, VOLUME_BUTTON = 1, 0
TEXT_PATH = "LevelTwoText.txt"
TEXT_BOX_PATHS = ["../../UI/TextBox.png", "../../UI/TextBoxArrow.png"]
DELAY_AT_START = 55
WARP_PATH = "../../Assets/Background/Warp.png"
LOCATION = "lake"
MAX_ALPHA = 255
FINAL_DELAY = 5

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
        self.hitbox = pygame.Rect(self.x + size[0] * 4, self.y + size[1] * 4, size[0] // 2, size[1] // 2)
        #player Pokemon
        self.player_pokemon = {
            0: Pokemon('Charmadillo', 150),
            1: Pokemon('Friolera', 25),
            2: Pokemon('Plumette', 20)
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

        # Check if player moved
        if self.x != self.old_x or self.y != self.old_y:
            self.moving = True
        else:
            self.moving = False

        # Check for collisions
        self.collide()

        # Update sprite properties
        self.y_sort = self.rect.centery
        self.image = MC.assets[self.facing][int(self.currImage) % self.maxFrames]

    def collide(self):
        # Check for collisions with all collidable sprites
        moved = False
        for sprite in self.collidable:
            if sprite.hitbox.colliderect(self.hitbox):
                if isinstance(sprite, BaseWarp):
                    sprite.warp()
                elif isinstance(sprite, Waterside):
                    sprite.event()
                # Move back to previous position if collision occurs
                elif not moved:
                    moved = True
                    self.x, self.y = self.old_x, self.old_y
                    self.rect.center = (self.x, self.y)
                    self.hitbox.center = (self.x + PLAYER_SIZE[0] // 4, self.y + PLAYER_SIZE[1] // 4)

    def heal_pokemon(self):
        for pokemon in self.player_pokemon.values():
            pokemon.heal()

    def toggleblock(self):
        self.blocked = not self.blocked

    def moveWater(self):
        checkCollide = self.game.collide if self.collidable == self.game.collideLand else self.game.collideLand if self.collidable == self.game.collide else None
        if checkCollide:
            if self.facing == LEFT:
                self.x -= BLOCK_SIZE * 2
            elif self.facing == RIGHT:
                self.x += BLOCK_SIZE * 2
            elif self.facing == UP:
                self.y -= BLOCK_SIZE * 2
            elif self.facing == DOWN:
                self.y += BLOCK_SIZE * 2

            self.rect.center = (self.x, self.y)
            self.hitbox.center = (self.x + PLAYER_SIZE[0] // 4, self.y + PLAYER_SIZE[1] // 4)
            for sprite in checkCollide:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.facing == LEFT:
                        self.x += BLOCK_SIZE * 2
                    elif self.facing == RIGHT:
                        self.x -= BLOCK_SIZE * 2
                    elif self.facing == UP:
                        self.y += BLOCK_SIZE * 2
                    elif self.facing == DOWN:
                        self.y -= BLOCK_SIZE * 2

                    self.rect.center = (self.x, self.y)
                    self.hitbox.center = (self.x + PLAYER_SIZE[0] // 4, self.y + PLAYER_SIZE[1] // 4)
                    print(sprite)
                    return False
            self.image = MC.assets[self.facing][0]
            self.currImage = 0
            return True
        return False



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


class Daniel(Entity):
    # Sound effects
    pygame.mixer.init()
    cry = pygame.mixer.Sound(POKEMON_CRY)
    cry.set_volume(GAME_VOLUME)

    def __init__(self, pos, image_paths, group, size, game, z=4):
        super().__init__(pos, group, size, z)
        self.game = game
        self.player = game.player
        self.img_index = 0

        # Scaling properties
        self.scale = 0.0
        self.target_scale = 8.0
        self.scaling_speed = 4.0  # Scale units per second
        self.scaling_complete = False

        # Load images
        self.original_images = []
        for path in image_paths:
            try:
                image = pygame.image.load(path).convert_alpha()
            except FileNotFoundError:
                image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                image.fill((255, 0, 0, 128))  # Semi-transparent red as error indicator
            self.original_images.append(image)

        # Position relative to player (always below)
        self.relative_y_offset = BLOCK_SIZE // 2 # Position below player

        # Initialize image and rect
        self.update_image()
        self.rect = self.image.get_rect(center=self.get_target_position())

        self.startShrink = True

    def get_target_position(self):
        """Calculate position directly below player"""
        return (self.player.x, self.player.y + self.relative_y_offset)

    def update_image(self):
        """Update scaled image based on current scale"""
        if not self.original_images:
            return

        # Choose image based on player's facing direction
        self.img_index = 1 if self.player.facing == RIGHT else 0 if self.player.facing == LEFT else self.img_index

        # Scale the image
        original_img = self.original_images[self.img_index]
        new_width = int(original_img.get_width() * self.scale)
        new_height = int(original_img.get_height() * self.scale)
        self.image = pygame.transform.scale(original_img, (new_width, new_height))

    def update_scale(self, dt):
        """Handle the scaling animation"""
        if not self.scaling_complete:
            self.scale = min(self.scale + self.scaling_speed * dt, self.target_scale)
            if self.scale >= self.target_scale:
                self.scaling_complete = True
                Daniel.cry.play()  # Play sound when fully grown
                self.game.inEvent = False
            self.update_image()

    def shrink_to_nothing(self, dt):
        """Animate the Pokemon shrinking to nothing"""
        if self.startShrink:
            self.scale = 1.0
            self.startShrink = False
        if self.scale > 0:
            self.scale = max(0, self.scale - self.scaling_speed * dt / 8)
            self.update_image()

            # Update position to stay below player while shrinking
            target_pos = self.get_target_position()
            self.x = target_pos[0]
            self.y = target_pos[1]

            # Update rect and sorting
            self.rect = self.image.get_rect(center=(self.x, self.y))
            self.y_sort = self.rect.centery
            return False  # Still shrinking
        else:
            self.kill()  # Remove sprite when fully shrunk
            self.cry.play()  # Play sound when fully shrunk
            self.game.inEvent = False
            self.game.madeADaniel = False
            self.game.player.z = 3
            return True   # Shrinking complete

    # Example usage in update method:
    def update(self, dt):
        if self.scaling_complete and not self.game.water:
            self.shrink_to_nothing(dt)
        else:
            # Update scaling animation
            self.update_scale(dt)

            # Always move to position below player
            target_pos = self.get_target_position()
            self.x = target_pos[0]
            self.y = target_pos[1]

            # Update facing direction to match player
            self.facing = self.player.facing

            # Update image based on player's facing direction
            if hasattr(self.player, 'facing'):
                if self.player.facing == LEFT:
                    self.image = pygame.transform.scale(self.original_images[0],
                                                        (int(BLOCK_SIZE * self.scale),
                                                         int(BLOCK_SIZE * self.scale)))
                elif self.player.facing == RIGHT:
                    self.image = pygame.transform.scale(self.original_images[1],
                                                        (int(BLOCK_SIZE * self.scale),
                                                         int(BLOCK_SIZE * self.scale)))
                else:
                    self.image = pygame.transform.scale(self.image,
                                                        (int(BLOCK_SIZE * self.scale),
                                                         int(BLOCK_SIZE * self.scale)))
            # Update rect and sorting
            self.rect = self.image.get_rect(center=(self.x, self.y))
            self.y_sort = self.rect.centery

