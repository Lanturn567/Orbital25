import sys
import math
import os

from pygame import SCALED
from pytmx.util_pygame import load_pygame
from Code.Entities.Trainer import *
from Code.support import *
from Code.LevelOneStage.LevelOne import LevelOneVolumeButton
from Code.Stages.Lake.Lake import *
from Code.sprites import *
from Code.entities import *
from Code.Save import *
from Code.Entities.Pokemon import Pokemon
from Code.Battle import Battle

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
FADE_IN_CHANGE_PER_FRAME = 36
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
LOST_TEXT = os.path.join(BASE_DIR, "HaventMetMom.txt")
PROF_TEXT = os.path.join(BASE_DIR, "HaventMetProf.txt")
DELAY_AT_START = 10
WARP_PATH = os.path.join(BASE_DIR, "../../../Assets/Background/Warp.png")

LOCATION = "home"
MAX_ALPHA = 255
FINAL_DELAY = 5

STAGES = {}

# Initialize pygame
pygame.init()
# screen = pygame.display.set_mode((MAX_X, MAX_Y), flags=SCALED, vsync=1) #Andre
screen = pygame.display.set_mode((MAX_X, MAX_Y)) #Rhysmond
pygame.display.set_caption("Home")

# pokemon frames
pokemon_frames = {
    'icons': import_folder_dict(os.path.join(BASE_DIR, '../../../Assets/Pokemon/icons')),
    'pokemon': monster_importer(4, 2, os.path.join(BASE_DIR, '../../../Assets/Pokemon/pokemon')),
    'ui': import_folder_dict(os.path.join(BASE_DIR, '../../../Assets/UI/ui'))
}

#CHANGE
pokemon_frames['outlines'] = outline_creator(pokemon_frames['pokemon'], 4)

# fonts
def get_font_path(*parts):
    return os.path.join(BASE_DIR, '..', '..', '..', 'Assets', 'Fonts', *parts)

# Load fonts using absolute paths
fonts = {
    'dialog': pygame.font.Font(get_font_path('PixeloidSans.ttf'), 12),
    'regular': pygame.font.Font(get_font_path('PixeloidSans.ttf'), 12),
    'small': pygame.font.Font(get_font_path('PixeloidSans.ttf'), 11),
    'bold': pygame.font.Font(get_font_path('dogicapixelbold.otf'), 13),
}

#CHANGE
#bg frames
bg_frames = import_folder_dict(os.path.join(BASE_DIR, '../../../Assets/backgrounds'))

class HomeEventWarp(EventWarp):
    #dir in ["left", "right", "up", "down"]
    def __init__(self, pos, stage, image, groups, game, loc, cond, dir, z=1):
        super().__init__(pos, stage, image, groups, game, loc, cond, z)
        self.dir = dir

    def makeEvent(self):
        StoryTextBox.init__text(LOST_TEXT)
        self.game.buttons[TEXT_BUTTON].reset()
        if self.dir in ["left", "right"]:
            self.game.player.x = self.rect.x
        else:
            self.game.player.y = self.rect.y
        self.game.inEvent = True
        self.afterEvent()

    def afterEvent(self):
        def checker():
            if self.game.textComplete:
                self.game.inEvent = False
                self.game.updateEvent = None
                if self.dir == "left":
                    self.game.player.x -= BLOCK_SIZE
                    self.game.player.facing = LEFT
                elif self.dir == "right":
                    self.game.player.x += BLOCK_SIZE
                    self.game.player.facing = RIGHT
                elif self.dir == "up":
                    self.game.player.y -= BLOCK_SIZE
                    self.game.player.facing = UP
                elif self.dir == "down":
                    self.game.player.y += BLOCK_SIZE
                    self.game.player.facing = DOWN
        self.game.updateEvent = checker



class HomeEventWarpPhaseTwo(EventWarp):
    #dir in ["left", "right", "up", "down"]
    def __init__(self, pos, stage, image, groups, game, loc, cond, dir, z=1):
        super().__init__(pos, stage, image, groups, game, loc, cond, z)
        self.val = 0
        self.dir = dir

    def makeEvent(self):
        StoryTextBox.init__text(LOST_TEXT if self.val == 0 else PROF_TEXT)
        self.game.buttons[TEXT_BUTTON].reset()
        if self.dir in ["left", "right"]:
            self.game.player.x = self.rect.x
        else:
            self.game.player.y = self.rect.y
        self.game.inEvent = True
        self.afterEvent()

    def warp(self):
        self.val = self.cond()
        if self.val == 2:
            super().warp()
        else:
            self.makeEvent()

    def afterEvent(self):
        def checker():
            if self.game.textComplete:
                self.game.inEvent = False
                self.game.updateEvent = None
                if self.dir == "left":
                    self.game.player.x -= BLOCK_SIZE
                    self.game.player.facing = LEFT
                elif self.dir == "right":
                    self.game.player.x += BLOCK_SIZE
                    self.game.player.facing = RIGHT
                elif self.dir == "up":
                    self.game.player.y -= BLOCK_SIZE
                    self.game.player.facing = UP
                elif self.dir == "down":
                    self.game.player.y += BLOCK_SIZE
                    self.game.player.facing = DOWN
        self.game.updateEvent = checker


class Home:
    tmx = load_pygame(TMX_PATH)

    def __init__(self, screen, start_pos, save):
        self.start_pos = start_pos
        self.screen = screen
        self.save = save
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

        #CHANGE
        self.dummy_monsters = {
            0: Pokemon('Finsta', 15),
            1: Pokemon('Atrox', 13),
            2: Pokemon('Larvea', 13),
            3: Pokemon('Pouch', 12),
        }


    def init_assets(self, start_pos):

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
            if obj.properties["pos"] in ["left"]:
                dir = obj.properties["dir"]
                HomeEventWarp((obj.x, obj.y), obj.properties["pos"], image=image, groups=(self.sprite_group, self.collide), game=self, z=2, dir=dir, loc=LOCATION, cond=self.save.seenMom)
            elif obj.properties["pos"] in ["right", "party", "gym", "lake"]:
                dir = obj.properties["dir"]
                HomeEventWarpPhaseTwo((obj.x, obj.y), obj.properties["pos"], image=image, groups=(self.sprite_group, self.collide), game=self, z=2, dir=dir, loc=LOCATION, cond=self.save.homeTest)
            else:
                BaseWarp((obj.x, obj.y), obj.properties["pos"], image=image, groups=(self.sprite_group, self.collide), game=self, loc=LOCATION, z=2)

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

        # Pokemon menu
        self.menu = Menu(self.player.player_pokemon, fonts, pokemon_frames)
        self.menu_open = False

        #CHANGE
        # Battle
        self.battle = Battle(self.player.player_pokemon, self.dummy_monsters, pokemon_frames, bg_frames['forest'], fonts)

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
                self.alpha = min(self.alpha + FADE_IN_CHANGE_PER_FRAME * dt * ANIM_SPEED , MAX_ALPHA)
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

    def input(self):
        keys = pygame.key.get_pressed()

        if self.textComplete and not self.inEvent and keys[pygame.K_RETURN] and not self.prev_keys[pygame.K_RETURN]:
            self.menu.open_sound.play()
            self.menu_open = not self.menu_open
            self.player.toggleblock()

        self.prev_keys = keys

    def run(self):
        self.init_assets(self.start_pos)
        pygame.mixer.music.load(HOME_MUSIC_PATH)
        pygame.mixer.music.set_volume(GAME_VOLUME)
        pygame.mixer.music.play(-1, 10, 5000)
        StoryTextBox.init__text(TEXT_PATH1 if self.start_pos in ["lake", "right", "left"] else TEXT_PATH2)
        StoryTextBox.init_images(TEXT_BOX_PATHS)
        LakeVolumeButton.init_images(VOL_BUTTON_PATHS)
        self.buttons = [LakeVolumeButton(MAX_X - 50, MAX_Y - 50, self)]
        self.buttons[VOLUME_BUTTON].first_toggle()


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
            self.redraw()

            if self.menu_open: self.menu.update(dt)
            #CHANGE
            if self.battle: self.battle.update(dt)

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
    save.updateStage(LOCATION.title())
    save.updatePos(START_POS)
    SaveSystem.write(save)
    game = Home(screen, START_POS, save)
    nextStage = game.run()
    while True:
        nextStage = checkExit(nextStage)

