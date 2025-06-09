import pygame
import random
import sys
import os
from Code.LevelTwoStage.LevelTwo import Entity, TEXT_BUTTON, ANIM_SPEED
from Code.LevelTwoStage.StoryTextBox import StoryTextBox
from Code.Entities.Database import *
from Code.Battle import Battle
from Code.support import *
from Code.Entities.Pokemon import Pokemon
from Code.timer import Timer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BLOCK_SIZE = 32
PLAYER_SIZE = (32, 64)
DOWN, LEFT, RIGHT, UP = 2, 0, 1, 3
dirs = {"left" : LEFT,
        "right" : RIGHT,
        "up" : UP,
        "down" : DOWN}
INTERACTABLE_BOUNDS = [2 * BLOCK_SIZE, 2 * BLOCK_SIZE]
TRAINER_PATHS = { "lanturn" : [os.path.join(BASE_DIR, '../../Assets/Players/walkLanturnLeft.png'),
                              os.path.join(BASE_DIR, '../../Assets/Players/walkLanturnRight.png'),
                              os.path.join(BASE_DIR, '../../Assets/Players/walkLanturnFront.png'),
                              os.path.join(BASE_DIR, '../../Assets/Players/walkLanturnBack.png')],
                  "blond" : [os.path.join(BASE_DIR, '../../Assets/Players/blond.png')],
                  "child" : [os.path.join(BASE_DIR, '../../Assets/Players/girl.png')],
                  "guide" : [os.path.join(BASE_DIR, '../../Assets/Players/fireman.png')],
                  "garden" : [os.path.join(BASE_DIR, '../../Assets/Players/grassman.png')],
                  "man" : [os.path.join(BASE_DIR, '../../Assets/Players/trainer.png')],
                  "purple" : [os.path.join(BASE_DIR, '../../Assets/Players/purplewoman.png')],
                  "trainer" : [os.path.join(BASE_DIR, '../../Assets/Players/trainer.png')],
                  "villager" : [os.path.join(BASE_DIR, '../../Assets/Players/villager.png')],
                  "water" : [os.path.join(BASE_DIR, '../../Assets/Players/waterwoman.png')],
                  "woman" : [os.path.join(BASE_DIR, '../../Assets/Players/woman.png')],
                  "fisher" : [os.path.join(BASE_DIR, '../../Assets/Players/fisher.png')],
                  "bell" : [os.path.join(BASE_DIR, '../../Assets/Players/bellman.png')],
                  "prof" : [os.path.join(BASE_DIR, '../../Assets/Players/prof.png')],
                  "old" : [os.path.join(BASE_DIR, '../../Assets/Players/old.png')],
                  "white" : [os.path.join(BASE_DIR, '../../Assets/Players/whitewoman.png')],
                  "suit" : [os.path.join(BASE_DIR, '../../Assets/Players/suit.png')],
                  "breeder" : [os.path.join(BASE_DIR, '../../Assets/Players/breederwoman.png')],
                  "fighter" : [os.path.join(BASE_DIR, '../../Assets/Players/fighterwoman.png')],
                  "elec" : [os.path.join(BASE_DIR, '../../Assets/Players/elecwoman.png')],
                  "backpack" : [os.path.join(BASE_DIR, '../../Assets/Players/backpackwoman.png')],
                  "lucy" : [os.path.join(BASE_DIR, '../../Assets/Players/lucy.png')],
                  "office" : [os.path.join(BASE_DIR, '../../Assets/Players/office.png')],
                  "waitress" : [os.path.join(BASE_DIR, '../../Assets/Players/waitress.png')],
                  "kid" : [os.path.join(BASE_DIR, '../../Assets/Players/kid.png')],
                  "nurse" : [os.path.join(BASE_DIR, '../../Assets/Players/waitress.png')],
                  "mart" : [os.path.join(BASE_DIR, '../../Assets/Players/suit.png')],
                  "gym1" : [os.path.join(BASE_DIR, '../../Assets/Players/waterwoman.png')],
                  "punk" : [os.path.join(BASE_DIR, '../../Assets/Players/punk.png')],
                  "moon" : [os.path.join(BASE_DIR, '../../Assets/Players/moon.png')],
                  "madam" : [os.path.join(BASE_DIR, '../../Assets/Players/madam.png')],
                  "skiier" : [os.path.join(BASE_DIR, '../../Assets/Players/skiier.png')],
                  "rhymond" : [os.path.join(BASE_DIR, '../../Assets/Players/rhymond.png')],
                  }
ANIM_SPEED = 4
ANIM_DIST = 3
AFTER_EVENT_DELAY = 4
TRAINER_EVENT_PATH = [os.path.join(BASE_DIR, '../../Code/Stages/Home/Home1.txt')]

# pokemon frames
pokemon_frames = {
    'icons': import_folder_dict(os.path.join(BASE_DIR, '../../Assets/Pokemon/icons')),
    'pokemon': monster_importer(4, 2, os.path.join(BASE_DIR, '../../Assets/Pokemon/pokemon')),
    'ui': import_folder_dict(os.path.join(BASE_DIR, '../../Assets/UI/ui')),
    'attacks': attack_importer(os.path.join(BASE_DIR, '../../Assets/attacks'))
}

#CHANGE
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

#CHANGE
#bg frames
bg_frames = import_folder_dict(os.path.join(BASE_DIR, '../../Assets/backgrounds'))

class Trainer(Entity):

    ini = False
    assets = {}

    def __init__(self, pos, groups, game, size, facing, name, type="furina", road=None, dis=0, text=None, z=2):
        if not Trainer.ini:
            Trainer.init_assets(TRAINER_PATHS)
            Trainer.ini = True
        super().__init__(pos, groups, size, z)
        self.game = game
        self.facing = dirs[facing]

        self.road = [] if not road else road
        if not road:
            for i in range(dis):
                self.road.append(self.facing)
            dir = self.facing + 1 if self.facing == LEFT or self.facing == DOWN else DOWN if self.facing == UP else LEFT
            for i in range(dis):
                self.road.append(dir)

        self.images = Trainer.assets[type]
        self.image = self.images[self.facing][self.currImage]
        self.currentStep = 0
        self.maxSteps = len(self.road)
        self.box = pygame.Rect(self.x, self.y, self.rect.width + INTERACTABLE_BOUNDS[0], self.rect.height + INTERACTABLE_BOUNDS[1])
        self.box.center = (self.x, self.y)

        if self.facing == LEFT:
            self.maxFrames = Trainer.leftFrames
        if self.facing == RIGHT:
            self.maxFrames = Trainer.rightFrames
        if self.facing == UP:
            self.maxFrames = Trainer.upFrames
        if self.facing == DOWN:
            self.maxFrames = Trainer.downFrames

        self.TRAINER_GO_SPEED = random.randint(2, 4) * BLOCK_SIZE

        #info from database
        self.name = name
        self.info = database[self.name]
        if not self.info:
            self.info = database["Default"]

        #GO event
        self.text = text if text else self.info["talk"]
        self.currText = 0
        self.maxTalks = len(self.text) if self.text[0].endswith(".txt") else 1
        self.ticker = 0
        self.inEvent = False
        self.delayAfterEvent = 0

        #pokemon
        self.dummy_monsters = {
            0: Pokemon('Finsta', 2),
            1: Pokemon('Atrox', 2),
            2: Pokemon('Larvea', 1),
            3: Pokemon('Pouch', 1)
        }

        self.defeated = False


    @classmethod
    def init_assets(cls, database):
        for key in database:
            paths = database[key]
            curr = []
            #or 4 spritesheets (4x1)
            if len(paths) > 1:
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
                    curr.append(frames)
            #Either 16 sprites in 1 spritesheet (4x4)
            else:
                try:
                    surface = pygame.image.load(paths[0])
                except FileNotFoundError:
                    surface = pygame.Surface(PLAYER_SIZE)
                    surface.fill((255, 255, 255))

                down = [surface.subsurface(pygame.Rect(16 + 64 * x, 0, PLAYER_SIZE[0], PLAYER_SIZE[1])) for x in [0, 1, 2, 3]]
                left = [surface.subsurface(pygame.Rect(16 + 64 * x, 64, PLAYER_SIZE[0], PLAYER_SIZE[1])) for x in [0, 1, 2, 3]]
                right = [surface.subsurface(pygame.Rect(16 + 64 * x, 128, PLAYER_SIZE[0], PLAYER_SIZE[1])) for x in [0, 1, 2, 3]]
                up = [surface.subsurface(pygame.Rect(16 + 64 * x, 64 * 3, PLAYER_SIZE[0], PLAYER_SIZE[1])) for x in [0, 1, 2, 3]]
                curr = [left, right, down, up]

            cls.assets[key] = curr

        cls.leftFrames = 4
        cls.rightFrames = 4
        cls.downFrames = 4
        cls.upFrames = 4


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

            elif self.box.colliderect(self.game.player.hitbox):
                if self.game.player.x > self.x and abs(self.game.player.y - self.y) < BLOCK_SIZE // 2:
                    self.facing = RIGHT
                elif self.game.player.x < self.x and abs(self.game.player.y - self.y) < BLOCK_SIZE // 2:
                    self.facing = LEFT
                elif self.game.player.y < self.y:
                    self.facing = UP
                elif self.game.player.y >= self.y:
                    self.facing = DOWN
                self.currImage = 0

    def collide(self):
        keys = pygame.key.get_pressed()
        if self.box.colliderect(self.game.player.hitbox) and not self.game.menu_open and keys[pygame.K_SPACE] and not self.game.inEvent and not self.inEvent and self.delayAfterEvent >= AFTER_EVENT_DELAY:
            self.inEvent = True
            self.game.inEvent = True
            self.makeEvent()

        # Check if text is finished and we were waiting to start the battle
        if self.inEvent and getattr(self, 'awaiting_battle', False) and self.game.textComplete and not self.defeated:
            self.start_battle()

    def update(self, dt):
        # Update position
        self.rect.center = (self.x, self.y)
        self.hitbox.center = (self.x, self.y + PLAYER_SIZE[1] // 4)
        if not self.inEvent and not self.game.inEvent:
            self.delayAfterEvent += 0 if self.delayAfterEvent >= AFTER_EVENT_DELAY else dt * ANIM_SPEED
        elif self.game.inEvent:
            self.delayAfterEvent = 0
        # Check for collisions
        if not self.inEvent and self.game.textComplete:
            self.move(dt)
            self.y_sort = self.rect.centery
            self.image = self.images[self.facing][int(self.currImage) % self.maxFrames]
        elif self.inEvent and self.game.textComplete:
            self.inEvent = False
            self.game.inEvent = False
            self.delayAfterEvent = 0


    def makeEvent(self):
        StoryTextBox.init__text(self.text[self.currText] if self.text[self.currText].endswith(".txt") else self.text)
        self.game.buttons[TEXT_BUTTON].reset()
        self.currText = self.currText + 1 if self.currText < self.maxTalks - 1 else self.currText

        self.awaiting_battle = True

    def start_battle(self):
        self.game.battle = Battle(
            player_pokemon=self.game.player.player_pokemon,
            opponent_pokemon=self.dummy_monsters,
            pokemon_frames=pokemon_frames,
            bg_surf=bg_frames['forest'],
            fonts=fonts,
            trainer=self,
            game=self.game
        )
        self.awaiting_battle = False  # Clear flag
        self.inEvent = False
        self.game.inEvent = False
        self.game.textComplete = False

