import sys
import os
import random
import math
from pytmx.util_pygame import load_pygame
from Code.Stages.Lake.Lake import *
from Code.Entities.Trainer import *
from Code.sprites import *
from Code.entities import *

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMX_PATH = os.path.join(BASE_DIR, "../../../Data/TilemapsPNG/Gym.tmx")
START_POS = "home"
DOWN, LEFT, RIGHT, UP = 2, 0, 1, 3
BLOCK_SIZE = 32
PLAYER_SIZE = (32, 64)
PLAYER_SPEED = BLOCK_SIZE // 3
MAX_SPEED = BLOCK_SIZE // 3 * 2
MAX_X, MAX_Y = 740, 493
MAX_FPS = 0
LEVEL_TWO_MUSIC_PATH = os.path.join(BASE_DIR, "../../../Audio/Gym.mp3")
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
TEXT_PATH1 = os.path.join(BASE_DIR, "Gym.txt")
TEXT_BOX_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/TextBox.png"),
                  os.path.join(BASE_DIR, "../../../Assets/UI/TextBoxArrow.png")]
VOL_BUTTON_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/NoMute.png"),
                    os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/Mute.png")]
DELAY_AT_START = 10
WARP_PATH = os.path.join(BASE_DIR, "../../../Assets/Background/Warp.png")
LOCATION = "gym"
MAX_ALPHA = 255
FINAL_DELAY = 5

# Spotlight constants
SPOTLIGHT_RADIUS = 90
SPOTLIGHT_ALPHA = 180
SPOTLIGHT_COUNT = 3  # Number of spotlights
# In the constants section (near the top of the file)
SPOTLIGHT_SPEED = 4.0  # Base speed multiplier (higher = faster)
SPOTLIGHT_SPEED_VARIATION = 1.5  # How much speed varies between spotlights
MIN_SPOTLIGHT_SPEED = 0.5  # Minimum speed any spotlight can have
MAX_SPOTLIGHT_SPEED = 3.0  # Maximum speed any spotlight can have

STAGES = {}

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((MAX_X, MAX_Y), flags=SCALED, vsync=1)
pygame.display.set_caption("Gym")


class Spotlight:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.positions = []
        self.angles = []
        self.speeds = []

        # Initialize multiple spotlights
        for _ in range(SPOTLIGHT_COUNT):
            self.positions.append([
                random.randint(0, width),
                random.randint(0, height)
            ])
            self.angles.append(random.uniform(0, 2 * math.pi))
            self.speeds.append(random.uniform(0.3, 0.7))

    def update(self, dt):
        # Then in the Spotlight class update method:
        # Update each spotlight's position
        for i in range(len(self.positions)):
            # Calculate movement with speed adjusted by dt for frame independence
            move_x = math.cos(self.angles[i]) * self.speeds[i] * SPOTLIGHT_SPEED * dt * 60
            move_y = math.sin(self.angles[i]) * self.speeds[i] * SPOTLIGHT_SPEED * dt * 60

            self.positions[i][0] += move_x
            self.positions[i][1] += move_y

        # Update each spotlight's position
        for i in range(len(self.positions)):
            # Move in current direction
            self.positions[i][0] += math.cos(self.angles[i]) * self.speeds[i] * dt * 60
            self.positions[i][1] += math.sin(self.angles[i]) * self.speeds[i] * dt * 60

            # Bounce off edges
            if self.positions[i][0] < 0 or self.positions[i][0] > self.width:
                self.angles[i] = math.pi - self.angles[i]
            if self.positions[i][1] < 0 or self.positions[i][1] > self.height:
                self.angles[i] = -self.angles[i]

            # Occasionally change direction
            if random.random() < 0.005:
                self.angles[i] += random.uniform(-0.5, 0.5)



    def draw(self, surface):
        self.surface.fill((0, 0, 0, 0))  # Clear with transparent

        # Draw dark overlay
        pygame.draw.rect(self.surface, (0, 0, 0, SPOTLIGHT_ALPHA), (0, 0, self.width, self.height))

        # Draw spotlights (circular cutouts)
        for pos in self.positions:
            pygame.draw.circle(
                self.surface,
                (0, 0, 0, 0),  # Transparent
                (int(pos[0]), int(pos[1])),
                SPOTLIGHT_RADIUS
            )

        # Blend with main surface
        surface.blit(self.surface, (0, 0))


class Spectator(Trainer):
    def move(self, dt):
        # Store previous position
        if not self.inEvent:
            dir = self.road[int(self.currentStep) % self.maxSteps] if self.road else self.facing
            if not self.box.colliderect(self.game.player.hitbox) and self.maxSteps:
                if dir == LEFT:
                    self.x -= dt * self.TRAINER_GO_SPEED
                    if self.facing == LEFT:
                        self.currImage += dt * ANIM_SPEED
                    else:
                        self.facing = LEFT
                        self.currImage = 0
                        self.maxFrames = Trainer.leftFrames

                elif dir == RIGHT:
                    self.x += dt * self.TRAINER_GO_SPEED
                    if self.facing == RIGHT:
                        self.currImage += dt * ANIM_SPEED
                    else:
                        self.facing = RIGHT
                        self.currImage = 0
                        self.maxFrames = Trainer.rightFrames

                elif dir == DOWN:
                    self.y += dt * self.TRAINER_GO_SPEED
                    if self.facing == DOWN:
                        self.currImage += dt * ANIM_SPEED
                    else:
                        self.facing = DOWN
                        self.maxFrames = Trainer.downFrames
                        self.currImage = 0

                elif dir == UP:
                    self.y -= dt * self.TRAINER_GO_SPEED
                    if self.facing == UP:
                        self.currImage += dt * ANIM_SPEED
                    else:
                        self.facing = UP
                        self.currImage = 0
                        self.maxFrames = Trainer.upFrames

                self.currentStep += dt * ANIM_DIST
                self.box.center = (self.x, self.y)


class GymWarp(BaseWarp):
    def __init__(self, pos, stage, image, groups, game, z=1):
        super().__init__(pos, stage, image, groups, game, z)

    def warp(self):
        self.game.nextStage = STAGES.get(self.stage)(self.game.screen)


class Gym:
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
        self.spotlight = Spotlight(MAX_X, MAX_Y)  # Initialize spotlight effect

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
        from Code.Stages.Home.Home import Home
        global STAGES
        STAGES = {
            "home": lambda screen: Home(screen, LOCATION),
        }
        # Ground tiles
        for x, y, surf in Gym.tmx.get_layer_by_name("Ground").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=pygame.transform.scale_by(surf, 2), groups=self.sprite_group, z=0)

        # 1warer tiles
        for x, y, surf in Gym.tmx.get_layer_by_name("Wall").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=pygame.transform.scale_by(surf, 2), groups=(self.sprite_group, self.collide), z=1)

        # Players
        for obj in Gym.tmx.get_layer_by_name("Player"):
            if obj.properties["pos"] == start_pos:
                self.player = MC((obj.x + 16, obj.y), PLAYER_PATHS, self.sprite_group, self.collide, self, size=PLAYER_SIZE, z=3)

        # Boundary
        for x, y, surf in Gym.tmx.get_layer_by_name("Floor").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=pygame.transform.scale_by(surf, 2), groups=(self.sprite_group, self.collide), z=2)

        # Boundary
        for x, y, surf in Gym.tmx.get_layer_by_name("Chairs").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=pygame.transform.scale_by(surf, 2), groups=(self.sprite_group, self.collide), z=2)

        #Movable
        for x, y, surf in Gym.tmx.get_layer_by_name("Movable").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=pygame.transform.scale_by(surf, 2), groups=(self.sprite_group), z=3)

        # Furniture
        for x, y, surf in Gym.tmx.get_layer_by_name("Furniture").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=pygame.transform.scale_by(surf, 2), groups=(self.sprite_group, self.collide), z=2)

        # Furniture
        for x, y, surf in Gym.tmx.get_layer_by_name("Exit").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=1)

        # Furniture
        for x, y, surf in Gym.tmx.get_layer_by_name("LeftSpec").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            type = random.choice([key for key in TRAINER_PATHS.keys()])
            Spectator(pos, dis=0, type=type, name="Spectator", groups=(self.sprite_group, self.collide, self.entities), game=self, size=PLAYER_SIZE, facing="left", z=3)

        # Furniture
        for x, y, surf in Gym.tmx.get_layer_by_name("RightSpec").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            type = random.choice([key for key in TRAINER_PATHS.keys()])
            Spectator(pos, dis=0, type=type, name="Spectator", groups=(self.sprite_group, self.collide, self.entities), game=self, size=PLAYER_SIZE, facing="right", z=3)

        # Furniture
        for x, y, surf in Gym.tmx.get_layer_by_name("UpSpec").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            type = random.choice([key for key in TRAINER_PATHS.keys()])
            Spectator(pos, dis=0, type=type, name="Spectator", groups=(self.sprite_group, self.collide, self.entities), game=self, size=PLAYER_SIZE, facing="up", z=3)

        # Furniture
        for x, y, surf in Gym.tmx.get_layer_by_name("DownSpec").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            type = random.choice([key for key in TRAINER_PATHS.keys()])
            Spectator(pos, dis=0, type=type, name="Spectator", groups=(self.sprite_group, self.collide, self.entities), game=self, size=PLAYER_SIZE, facing="down", z=3)

        # Warps
        for obj in Gym.tmx.get_layer_by_name("Warps"):
            GymWarp((obj.x, obj.y), obj.properties["pos"], image=pygame.image.load(WARP_PATH), groups=(self.sprite_group, self.collide), game=self, z=1)

        # Trainers
        for obj in Gym.tmx.get_layer_by_name("Trainers"):
            facing = obj.properties["dir"]
            type = obj.type
            dis = obj.properties["dis"]
            Trainer((obj.x + 16, obj.y), name=obj.name, dis=dis, type=type, groups=(self.sprite_group, self.collide, self.entities), game=self, size=PLAYER_SIZE, facing=facing, z=3)

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
        # Update player
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
        StoryTextBox.init__text(TEXT_PATH1)
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

                # Update and draw spotlight effect
                self.spotlight.update(dt)
                self.spotlight.draw(self.screen)

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
    game = Gym(screen, START_POS)
    nextStage = game.run()
    while True:
        nextStage = checkExit(nextStage)