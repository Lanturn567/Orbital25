import sys
import os
from pytmx.util_pygame import load_pygame
from Code.Stages.Lake.Lake import *
from Code.Entities.Trainer import *

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMX_PATH = os.path.join(BASE_DIR, "../../../Data/TilemapsPNG/Home.tmx")
START_POS = "home"
DOWN, LEFT, RIGHT, UP = 2, 0, 1, 3
BLOCK_SIZE = 32
PLAYER_SIZE = (32, 64)
PLAYER_SPEED = BLOCK_SIZE // 3
MAX_SPEED = BLOCK_SIZE * 2 // 3
MAX_X, MAX_Y = 740, 493
MAX_FPS = 60
LEVEL_TWO_MUSIC_PATH = os.path.join(BASE_DIR, "../../../Audio/Home.mp3")
FADE_LEVEL = 0
FADE_CHANGE_PER_FRAME = 12
PLAYER_PATHS = [os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkLeft.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkRight.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkFront.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkBack.png')]
INTERACTABLE_BOUNDS = [BLOCK_SIZE, BLOCK_SIZE]


GAME_VOLUME = 0.3
ANIM_SPEED = 8

DELAY_AFTER_CLICK = 4
TEXT_BOX_POS = (65, MAX_Y - 140)
TEXT_BUTTON, VOLUME_BUTTON = 1, 0
TEXT_PATH1 = os.path.join(BASE_DIR, "Dawn.txt")
TEXT_EVENTS_PATHS = ["DawnEvent1.txt", "DawnEvent2.txt"]
TEXT_BOX_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/TextBox.png"),
                  os.path.join(BASE_DIR, "../../../Assets/UI/TextBoxArrow.png")]
VOL_BUTTON_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/NoMute.png"),
                    os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/Mute.png")]
DELAY_AT_START = 10
WARP_PATH = os.path.join(BASE_DIR, "../../../Assets/Background/Warp.png")
LOCATION = "dawn"
MAX_ALPHA = 255
FINAL_DELAY = 5

STAGES = {}

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((MAX_X, MAX_Y))
pygame.display.set_caption("Dawn")


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


class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, groups, size, z=2):
        super().__init__(groups)
        self.z = z
        self.facing = DOWN
        self.currImage = 0
        self.x = pos[0]
        self.y = pos[1]
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        center = (self.x, self.y)
        self.rect.center = center
        self.hitbox = pygame.Rect(center[0], center[1], size[0], size[1])
        self.y_sort = self.rect.centery

    def input(self):
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
        self.hitbox = pygame.Rect(self.x + size[0] * 15 // 32, self.y + size[1] * 15 // 32, size[0] // 8, size[1] // 8)

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
        if self.game.textComplete and not self.game.inEvent:
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
        self.currImage += ANIM_SPEED * dt
        self.image = AnimatedSprite.assets[int(self.currImage) % AnimatedSprite.length]



class Warp(Sprite):
    def __init__(self, pos, stage_name, image, groups, game, z=1):
        super().__init__(pos, image, groups, z)
        self.game = game
        self.stage_name = stage_name
        self.hitbox = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)

    def warp(self):
        self.game.nextStage = STAGES.get(self.stage_name)(self.game.screen)

class Dawn:
    tmx = load_pygame(TMX_PATH)

    def __init__(self, screen, start_pos):
        self.start_pos = start_pos
        self.screen = screen
        self.sprite_group = AllSprites()
        self.collide = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.buttons = []
        self.alpha = 255
        self.rect = self.screen.get_rect()
        self.fadeInSurface = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)

        self.ticker = 0

        self.textComplete = False
        self.boxFinished = False
        self.isClicked = False
        self.clickDelay = 0

        self.inEvent = False
        self.updateEvent = None


        self.nextStage = None
        self.stageDone = False
        self.finalDelay = 0


    def init_assets(self, start_pos):
        from Code.Stages.Home import Home
        global STAGES
        STAGES = {
            "home": lambda screen: Home(screen, LOCATION),
        }

        # Ground tiles
        for x, y, surf in Dawn.tmx.get_layer_by_name("Ground").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=pygame.transform.scale_by(surf, 2), groups=self.sprite_group, z=0)

        # 1warer tiles
        for x, y, surf in Dawn.tmx.get_layer_by_name("Wall").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=pygame.transform.scale_by(surf, 2), groups=(self.sprite_group, self.collide), z=3)

        # Players
        for obj in Dawn.tmx.get_layer_by_name("Players"):
            if obj.properties["pos"] == start_pos:
                self.player = MC((obj.x + 16, obj.y), PLAYER_PATHS, self.sprite_group, self.collide, self, size=PLAYER_SIZE, z=3)

        # Boundary
        for x, y, surf in Dawn.tmx.get_layer_by_name("Boundary").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=pygame.transform.scale_by(surf, 2), groups=(self.sprite_group, self.collide), z=2)

        #Movable
        for x, y, surf in Dawn.tmx.get_layer_by_name("Movable").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=pygame.transform.scale_by(surf, 2), groups=self.sprite_group, z=2)

        # Furniture
        for x, y, surf in Dawn.tmx.get_layer_by_name("Furniture").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=pygame.transform.scale_by(surf, 2), groups=(self.sprite_group, self.collide), z=3)

        # Warps
        for obj in Dawn.tmx.get_layer_by_name("Warps"):
            Warp((obj.x, obj.y), obj.properties["pos"], image=pygame.image.load(WARP_PATH), groups=(self.sprite_group, self.collide), game=self, z=1)

        # Trainers
        for obj in Dawn.tmx.get_layer_by_name("Trainers"):
            facing = obj.properties["dir"]
            type = obj.type
            dis = obj.properties["dis"]
            Trainer((obj.x + 16, obj.y), dis=dis, type=type, groups=(self.sprite_group, self.collide, self.entities), game=self, size=PLAYER_SIZE, text=TEXT_EVENTS_PATHS, facing=facing, z=3)

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
                self.alpha = min(self.alpha + FADE_CHANGE_PER_FRAME * dt * ANIM_SPEED, MAX_ALPHA)

            if self.alpha >= MAX_ALPHA and self.finalDelay >= FINAL_DELAY:
                self.stageDone = True
            elif self.alpha >= MAX_ALPHA:
                self.finalDelay += dt * ANIM_SPEED

    def update_game_state(self, dt):
        #update player
        keys = pygame.key.get_pressed()
        for entity in self.entities:
            entity.collide()

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

    def redraw(self):
        # Draw buttons
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

        if self.updateEvent:
            self.updateEvent()

    def run(self):
        self.init_assets(self.start_pos)
        pygame.mixer.music.load(LEVEL_TWO_MUSIC_PATH)
        pygame.mixer.music.set_volume(GAME_VOLUME)
        pygame.mixer.music.play(-1, 10, 5000)
        StoryTextBox.init__text(TEXT_PATH)
        StoryTextBox.init_images(TEXT_BOX_PATHS)
        LakeVolumeButton.init_images(VOL_BUTTON_PATHS)
        self.buttons = [LakeVolumeButton(MAX_X - 50, MAX_Y - 50, self)]

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
                self.screen.fill("black")
                self.sprite_group.update(dt)
                self.sprite_group.draw(self.player.rect.center)
                self.redraw()
            self.fade(dt)
            pygame.display.flip()


        if self.nextStage:
            return self.nextStage
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
    game = Dawn(screen, START_POS)
    nextStage = game.run()
    while True:
        nextStage = checkExit(nextStage)

