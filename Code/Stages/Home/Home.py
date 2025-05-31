import sys
import math
import os

from pygame import SCALED
from pytmx.util_pygame import load_pygame
from Code.Entities.Trainer import *
from Code.support import *
from Code.LevelOneStage.LevelOne import LevelOneVolumeButton
from Code.sprites import *
from Code.entities import *
from Code.Entities.Pokemon import Pokemon

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMX_PATH = os.path.join(BASE_DIR, "../../../Data/TilemapsPNG/Home.tmx")
START_POS = "lake"
DOWN, LEFT, RIGHT, UP = 2, 0, 1, 3
BLOCK_SIZE = 32
PLAYER_SIZE = (32, 64)
PLAYER_SPEED = BLOCK_SIZE // 3
MAX_SPEED = BLOCK_SIZE * 2 // 3
MAX_X, MAX_Y = 740, 493
MAX_FPS = 0
HOME_MUSIC_PATH = os.path.join(BASE_DIR, "../../../Audio/Home.mp3")
FADE_LEVEL = 0
FADE_CHANGE_PER_FRAME = 12
PLAYER_PATHS = [os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkLeft.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkRight.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkFront.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkBack.png')]
TREE_PATH = [os.path.join(BASE_DIR, '../../../Assets/Background/Tree.png')]
INTERACTABLE_BOUNDS = [BLOCK_SIZE, BLOCK_SIZE]
VOL_BUTTON_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/NoMute.png"),
                    os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/Mute.png")]

GAME_VOLUME = 0.3
ANIM_SPEED = 8
FLOAT_SPEED = BLOCK_SIZE // 3
FLOAT_INTERVAL = 0.4
FLOAT_LENGTH = BLOCK_SIZE
DIST_FROM_PLAYER = BLOCK_SIZE * 15
POKEMON_CRY = os.path.join(BASE_DIR, "../../../Audio/Poke.wav")
BIG_POKEMON_SIZE = (64, 64)
SMALL_POKEMON_SIZE = (32, 32)

DELAY_AFTER_CLICK = 4
TEXT_BOX_POS = (65, MAX_Y - 140)
TEXT_BUTTON, VOLUME_BUTTON = 1, 0
TEXT_PATH1 = os.path.join(BASE_DIR, "Home1.txt")
TEXT_PATH2 = os.path.join(BASE_DIR, "Home2.txt")
TEXT_BOX_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/TextBox.png"),
                  os.path.join(BASE_DIR, "../../../Assets/UI/TextBoxArrow.png")]
DELAY_AT_START = 10
WARP_PATH = os.path.join(BASE_DIR, "../../../Assets/Background/Warp.png")
LOCATION = "home"
MAX_ALPHA = 255
FINAL_DELAY = 5

STAGES = {}

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((MAX_X, MAX_Y), flags=SCALED, vsync=1) #Andre
# screen = pygame.display.set_mode((MAX_X, MAX_Y)) #Rhysmond
pygame.display.set_caption("Home")

class LevelTwoVolumeButton(LevelOneVolumeButton):

    def toggle_volume(self):
        pygame.mixer.music.set_volume(0 if self.playing else GAME_VOLUME)
        StoryTextBox.clickSound.set_volume(0 if self.playing else GAME_VOLUME)
        self.playing = not self.playing
        self.update_image()

    def update_image(self):
        self.image_idx = 1 if not self.playing else 0


class HomeWarp(BaseWarp):

    def __init__(self, pos, stage, image, groups, game, z=1):
        super().__init__(pos, stage, image, groups, game, z)

    def warp(self):
        self.game.nextStage = STAGES.get(self.stage)(self.game.screen)


class Home:
    tmx = load_pygame(TMX_PATH)

    def __init__(self, screen, start_pos):
        self.start_pos = start_pos
        self.screen = screen
        self.sprite_group = AllSprites()
        self.collide = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
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
        from Code.Stages.Right.Right import Right
        from Code.Stages.Left.Left import Left
        from Code.Stages.Lake.Lake import Lake
        from Code.Stages.House.House import House
        from Code.Stages.Gym.Gym import Gym
        from Code.Stages.Party.Party import Party
        from Code.Stages.Dawn.Dawn import Dawn
        from Code.Stages.Blue.Blue import Blue
        from Code.Stages.Mart.Mart import Mart

        global STAGES
        STAGES = {
            "lake": lambda screen: Lake(screen, LOCATION),
            "right": lambda screen: Right(screen, LOCATION),
            "left": lambda screen: Left(screen, LOCATION),
            "house": lambda screen: House(screen, LOCATION),
            "gym": lambda screen: Gym(screen, LOCATION),
            "party": lambda screen: Party(screen, LOCATION),
            "dawn": lambda screen: Dawn(screen, LOCATION),
            "blue": lambda screen: Blue(screen, LOCATION),
            "mart": lambda screen: Mart(screen, LOCATION)
        }

        # Ground tiles
        for x, y, surf in Home.tmx.get_layer_by_name("Ground").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=0)

        # Players
        for obj in Home.tmx.get_layer_by_name("Player"):
            if obj.properties["pos"] == start_pos:
                self.player = MC((obj.x + 16, obj.y), PLAYER_PATHS, self.sprite_group, self.collide, self, size=PLAYER_SIZE, z=3)

        # Grass tiles
        for x, y, surf in Home.tmx.get_layer_by_name("Road").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=1)

        # Trees
        tree_image = pygame.image.load(TREE_PATH[0])
        for x, y, surf in Home.tmx.get_layer_by_name("Grass").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            tree = Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.collide), z=3)

        # Flowers
        for x, y, surf in Home.tmx.get_layer_by_name("Flowers").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=2)

        # Flowers
        for x, y, surf in Home.tmx.get_layer_by_name("Doors").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=2)

        # Warps
        for obj in Home.tmx.get_layer_by_name("Warps"):
            image = pygame.image.load(WARP_PATH)
            if obj.properties["size"] == "small":
                image = pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE))
            HomeWarp((obj.x, obj.y), obj.properties["pos"], image=image, groups=(self.sprite_group, self.collide), game=self, z=2)

        # Trees
        for x, y, surf in Home.tmx.get_layer_by_name("Buildings").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            building = Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.collide), z=3)

        # Trees
        for x, y, surf in Home.tmx.get_layer_by_name("TallBuildings").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            building = Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=4)


        # Trainers
        for obj in Home.tmx.get_layer_by_name("Trainers"):
            facing = obj.properties["dir"]
            type = obj.type
            dis = obj.properties["dis"]
            name = obj.name
            Trainer((obj.x + 16, obj.y), dis=dis, name=name, type=type, groups=(self.sprite_group, self.collide, self.entities), game=self, size=PLAYER_SIZE, facing=facing, z=3)

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
                self.alpha = min(self.alpha + FADE_CHANGE_PER_FRAME * dt * ANIM_SPEED , MAX_ALPHA)

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
        pygame.mixer.music.load(HOME_MUSIC_PATH)
        pygame.mixer.music.set_volume(GAME_VOLUME)
        pygame.mixer.music.play(-1, 10, 5000)
        StoryTextBox.init__text(TEXT_PATH1 if self.start_pos in ["lake", "right", "left"] else TEXT_PATH2)
        StoryTextBox.init_images(TEXT_BOX_PATHS)
        LevelTwoVolumeButton.init_images(VOL_BUTTON_PATHS)
        self.buttons = [LevelTwoVolumeButton(MAX_X - 50, MAX_Y - 50, self)]

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
    game = Home(screen, START_POS)
    nextStage = game.run()
    while True:
        nextStage = checkExit(nextStage)

