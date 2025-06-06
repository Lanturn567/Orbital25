import pygame
import sys
import math
import random
import os

from pygame import SCALED
from pytmx.util_pygame import load_pygame
from Code.LevelTwoStage.StoryTextBox import StoryTextBox
from Code.LevelOneStage.LevelOne import LevelOneVolumeButton
from Code.Opening.Opening import BGAsset
from Code.Entities.Trainer import Trainer
from Code.sprites import *
from Code.entities import *
from Code.Save import *

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMX_PATH = os.path.join(BASE_DIR, "../../../Data/TilemapsPNG/LevelTwo-TileMap.tmx")
START_POS = "mountain"
DOWN, LEFT, RIGHT, UP = 2, 0, 1, 3
BLOCK_SIZE = 32
PLAYER_SIZE = (32, 64)
SWAY_SPEED = BLOCK_SIZE
SWAY_INTERVAL = 2
SWAY_LENGTH = BLOCK_SIZE
SWAY_DELAY = 15
PLAYER_SPEED = BLOCK_SIZE // 3
MAX_SPEED = BLOCK_SIZE // 3 * 2
MAX_X, MAX_Y = 740, 493
MAX_FPS = 0
LEVEL_TWO_MUSIC_PATH = os.path.join(BASE_DIR, "../../../Audio/LevelTwoBGM.mp3")
FADE_LEVEL = 100
FADE_CHANGE_PER_FRAME = 6
FADE_IN_CHANGE_PER_FRAME = 18
WATER_PATHS = [os.path.join(BASE_DIR, '../../../Assets/Water/0.png'),
               os.path.join(BASE_DIR, '../../../Assets/Water/1.png'),
               os.path.join(BASE_DIR, '../../../Assets/Water/2.png'),
               os.path.join(BASE_DIR, '../../../Assets/Water/3.png')]
PLAYER_PATHS = [os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkLeft.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkRight.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkFront.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkBack.png')]
TREE_PATH = [os.path.join(BASE_DIR, '../../../Assets/Background/Tree.png')]
LEAF_PATH = [os.path.join(BASE_DIR, '../../../Assets/Background/Leaf.png')]
POKEMON_PATHS = [os.path.join(BASE_DIR, '../../../Assets/Pokemon/pokeL.png'), os.path.join(BASE_DIR, '../../../Assets/Pokemon/pokeR.png')]
VOL_BUTTON_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/NoMute.png"),
                    os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/Mute.png")]
GAME_VOLUME = 0.3
ANIM_SPEED = 8

DELAY_AFTER_CLICK = 4
TEXT_BOX_POS = (65, MAX_Y - 140)
TEXT_BUTTON, VOLUME_BUTTON = 1, 0
TEXT_PATH = os.path.join(BASE_DIR, "Lake.txt")
TEXT_BOX_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/TextBox.png"),
                  os.path.join(BASE_DIR, "../../../Assets/UI/TextBoxArrow.png")]
DELAY_AT_START = 10
WARP_PATH = os.path.join(BASE_DIR, "../../../Assets/Background/Warp.png")
LOCATION = "lake"
MAX_ALPHA = 255
FINAL_DELAY = 5

RAIN_COLOR = (173, 216, 230)  # Light blue
RAIN_WIDTH = 3
RAIN_HEIGHT = 10
RAIN_COUNT = 100
RAIN_SPEED = 250


STAGES = {}


# Initialize pygame
pygame.init()
# screen = pygame.display.set_mode((MAX_X, MAX_Y), flags=SCALED, vsync=1) #Andre
screen = pygame.display.set_mode((MAX_X, MAX_Y)) #Rhysmond
pygame.display.set_caption("Lake")

# pokemon frames
pokemon_frames = {
    'icons': import_folder_dict(os.path.join(BASE_DIR, '../../../Assets/Pokemon/icons')),
    'pokemon': monster_importer(4, 2, os.path.join(BASE_DIR, '../../../Assets/Pokemon/pokemon')),
    'ui': import_folder_dict(os.path.join(BASE_DIR, '../../../Assets/UI/ui'))
}
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

class LakeVolumeButton(LevelOneVolumeButton):

    def first_toggle(self):
        if self.game.save.getMuted():
            pygame.mixer.music.set_volume(0 if self.playing else GAME_VOLUME)
            StoryTextBox.clickSound.set_volume(0 if self.playing else GAME_VOLUME)
            BaseWarp.warpSound.set_volume(0 if self.playing else GAME_VOLUME)
            Menu.open_sound.set_volume(0 if self.playing else GAME_VOLUME)
            Menu.click_sound.set_volume(0 if self.playing else GAME_VOLUME)
            Menu.select_sound.set_volume(0 if self.playing else GAME_VOLUME)
            Daniel.cry.set_volume(0 if self.playing else GAME_VOLUME)
            self.playing = not self.playing
            self.update_image()

    def toggle_volume(self):
        pygame.mixer.music.set_volume(0 if self.playing else GAME_VOLUME)
        StoryTextBox.clickSound.set_volume(0 if self.playing else GAME_VOLUME)
        BaseWarp.warpSound.set_volume(0 if self.playing else GAME_VOLUME)
        Menu.open_sound.set_volume(0 if self.playing else GAME_VOLUME)
        Menu.click_sound.set_volume(0 if self.playing else GAME_VOLUME)
        Menu.select_sound.set_volume(0 if self.playing else GAME_VOLUME)
        Daniel.cry.set_volume(0 if self.playing else GAME_VOLUME)
        self.game.save.updateMuted()
        self.playing = not self.playing
        self.update_image()

    def update_image(self):
        self.image_idx = 1 if not self.playing else 0


class Lake:
    tmx = load_pygame(TMX_PATH)

    def __init__(self, screen, start_pos, save):
        self.start_pos = start_pos
        self.screen = screen
        self.save = save
        self.sprite_group = AllSprites()
        self.collide = pygame.sprite.Group()
        self.collideLand = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.leaves = []
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

        self.raindrops = []

        self.water = False
        self.daniel = None
        self.madeADaniel = False


    def init_assets(self, start_pos):

        # Ground tiles
        for x, y, surf in Lake.tmx.get_layer_by_name("Ground").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.collideLand), z=1)

        # 1warer tiles
        for x, y, surf in Lake.tmx.get_layer_by_name("Water").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            AnimatedSprite(pos, WATER_PATHS, groups=(self.sprite_group, self.collide), z=0)

        # Players
        for obj in Lake.tmx.get_layer_by_name("Player"):
            if obj.properties["pos"] == start_pos:
                self.player = MC((obj.x + 16, obj.y), PLAYER_PATHS, self.sprite_group, self.collide, self, size=PLAYER_SIZE, z=3)

        # Grass tiles
        for x, y, surf in Lake.tmx.get_layer_by_name("Grass").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=3)

        # Trees
        #tree_image = pygame.image.load(TREE_PATH[0])
        for x, y, surf in Lake.tmx.get_layer_by_name("LowerTrees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            tree = Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.collide), z=3)

        # Trees
        #tree_image = pygame.image.load(TREE_PATH[0])
        for x, y, surf in Lake.tmx.get_layer_by_name("UpperTrees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            tree = Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=3)

        # Trees
        #tree_image = pygame.image.load(TREE_PATH[0])
        for x, y, surf in Lake.tmx.get_layer_by_name("Trunk").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            tree = Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=2)

        for x, y, surf in Lake.tmx.get_layer_by_name("Waterside").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=2)

        if self.save.gotDaniel():
            for x, y, surf in Lake.tmx.get_layer_by_name("Surfable").tiles():
                image = pygame.image.load(WARP_PATH)
                pos = (x * BLOCK_SIZE + 8, y * BLOCK_SIZE)
                image = pygame.transform.scale_by(image, 0.75)
                Waterside(pos=pos, image=image , game=self, groups=(self.sprite_group, self.collideLand, self.collide), z=2)

        for x, y, surf in Lake.tmx.get_layer_by_name("Base").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=1)

        #tree_image = pygame.image.load(TREE_PATH[0])
        for x, y, surf in Lake.tmx.get_layer_by_name("Buildings").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.collide), z=2)

        # Warps
        for obj in Lake.tmx.get_layer_by_name("Warps"):
            BaseWarp((obj.x, obj.y), obj.properties["pos"], image=pygame.image.load(WARP_PATH), groups=(self.sprite_group, self.collide), game=self, loc=LOCATION, z=2)

        #def __init__(self, pos, paths, group, game, size, road, z=2):
        # Trainers
        for obj in Lake.tmx.get_layer_by_name("Trainers"):
            if not obj.type == "furina":
                facing = obj.properties["dir"]
                type = obj.type
                dis = obj.properties["dis"]
                Trainer((obj.x + 16, obj.y), name=obj.name, dis=dis, type=type, groups=(self.sprite_group, self.collide, self.entities), game=self, size=PLAYER_SIZE, facing=facing, z=3)

        # Pokemon menu
        self.menu = Menu(self.player.player_pokemon, fonts, pokemon_frames)
        self.menu_open = False

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

        if self.water and not self.madeADaniel:
            self.player.z = 5
            self.madeADaniel = True
            self.player.collidable = self.collideLand
            self.daniel = Daniel(
                pos=(self.player.x, self.player.y + BLOCK_SIZE * 1.5),  # Start below player
                image_paths=POKEMON_PATHS,
                group=self.sprite_group,
                size=(BLOCK_SIZE, BLOCK_SIZE),
                game=self,
                z=4
            )
        elif not self.water:
            self.player.collidable = self.collide

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
        # Draw rain behind everything else
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

    def run(self):
        self.init_assets(self.start_pos)
        pygame.mixer.music.load(LEVEL_TWO_MUSIC_PATH)
        pygame.mixer.music.set_volume(GAME_VOLUME)
        pygame.mixer.music.play(-1, 10, 5000)
        StoryTextBox.init__text(TEXT_PATH)
        StoryTextBox.init_images(TEXT_BOX_PATHS)
        LakeVolumeButton.init_images(VOL_BUTTON_PATHS)
        Leaf.init_images(LEAF_PATH)
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
            self.redraw(dt)
            if self.menu_open: self.menu.update(dt)

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
    game = Lake(screen, START_POS, save)
    nextStage = game.run()
    while True:
        nextStage = checkExit(nextStage)

