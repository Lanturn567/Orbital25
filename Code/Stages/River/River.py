import sys
import os
from pytmx.util_pygame import load_pygame
from Code.Stages.Lake.Lake import *
from Code.Entities.Trainer import *
from Code.sprites import *
from Code.entities import *
from Code.Save import *

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMX_PATH = os.path.join(BASE_DIR, "../../../Data/TilemapsPNG/River.tmx")
START_POS = "left"
DOWN, LEFT, RIGHT, UP = 2, 0, 1, 3
BLOCK_SIZE = 32
PLAYER_SIZE = (32, 64)
PLAYER_SPEED = BLOCK_SIZE // 3
MAX_SPEED = BLOCK_SIZE // 3 * 2
MAX_X, MAX_Y = 740, 493
MAX_FPS = 0
LEVEL_TWO_MUSIC_PATH = os.path.join(BASE_DIR, "../../../Audio/River.mp3")
FADE_LEVEL = 0
FADE_CHANGE_PER_FRAME = 12
FADE_IN_CHANGE_PER_FRAME = 36
PLAYER_PATHS = [os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkLeft.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkRight.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkFront.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkBack.png')]
INTERACTABLE_BOUNDS = [BLOCK_SIZE, BLOCK_SIZE]
SNORLAX_PATHS = [os.path.join(BASE_DIR, '../../../Assets/Pokemon/SnorlaxL.png'),
                 os.path.join(BASE_DIR, '../../../Assets/Pokemon/SnorlaxR.png')]
SNORLAX_SIZE = (384, 384)
SNORLAX_SOUND = os.path.join(BASE_DIR, '../../../Audio/Snorlax.wav')


GAME_VOLUME = 0.3
ANIM_SPEED = 8

DELAY_AFTER_CLICK = 4
TEXT_BOX_POS = (65, MAX_Y - 140)
TEXT_BUTTON, VOLUME_BUTTON = 1, 0
TEXT_PATH1 = os.path.join(BASE_DIR, "River.txt")
TEXT_BOX_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/TextBox.png"),
                  os.path.join(BASE_DIR, "../../../Assets/UI/TextBoxArrow.png")]
VOL_BUTTON_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/NoMute.png"),
                    os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/Mute.png")]
DELAY_AT_START = 10
WARP_PATH = os.path.join(BASE_DIR, "../../../Assets/Background/Warp.png")
LOCATION = "river"
MAX_ALPHA = 255
FINAL_DELAY = 5

STAGES = {}

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((MAX_X, MAX_Y))
pygame.display.set_caption("River")

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

class RiverVolumeButton(LakeVolumeButton):

    def first_toggle(self):
        if self.game.save.getMuted():
            pygame.mixer.music.set_volume(0 if self.playing else GAME_VOLUME)
            StoryTextBox.clickSound.set_volume(0 if self.playing else GAME_VOLUME)
            BaseWarp.warpSound.set_volume(0 if self.playing else GAME_VOLUME)
            Menu.open_sound.set_volume(0 if self.playing else GAME_VOLUME)
            Menu.click_sound.set_volume(0 if self.playing else GAME_VOLUME)
            Menu.select_sound.set_volume(0 if self.playing else GAME_VOLUME)
            Daniel.cry.set_volume(0 if self.playing else GAME_VOLUME)
            Snorlax.sound.set_volume(0 if self.playing else GAME_VOLUME)
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
        Snorlax.sound.set_volume(0 if self.playing else GAME_VOLUME)
        self.game.save.updateMuted()
        self.playing = not self.playing
        self.update_image()

class Snorlax(Entity):

    ini = False
    assets = {}

    def __init__(self, pos, groups, game, size, facing, name, type="furina", road=None, dis=0, text=None, z=2):
        if not Snorlax.ini:
            Snorlax.init_assets(SNORLAX_PATHS)
            Snorlax.ini = True
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

        self.images = Snorlax.assets
        self.image = self.images[self.facing]
        self.currentStep = 0
        self.maxSteps = len(self.road)
        self.box = pygame.Rect(self.x, self.y, self.rect.width + INTERACTABLE_BOUNDS[0] * 2, self.rect.height + INTERACTABLE_BOUNDS[1] * 2)
        self.hitbox = pygame.Rect(self.x, self.y, self.rect.width, self.rect.height)
        self.hitbox.center = (self.x, self.y)
        self.box.center = (self.x, self.y)

        if self.facing == LEFT:
            self.maxFrames = Snorlax.leftFrames
        if self.facing == RIGHT:
            self.maxFrames = Snorlax.rightFrames
        if self.facing == UP:
            self.maxFrames = Snorlax.upFrames
        if self.facing == DOWN:
            self.maxFrames = Snorlax.downFrames

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


    @classmethod
    def init_assets(cls, paths):
        cls.assets = []
        for path in paths:
            #images 192 x 192 so scale by 2x
            curr = pygame.image.load(path)
            curr = pygame.transform.scale_by(curr, 2)
            curr = pygame.transform.rotate(curr, -50)
            cls.assets.append(curr)

        cls.leftFrames = 1
        cls.rightFrames = 1
        cls.downFrames = 0
        cls.upFrames = 0

        cls.sound = pygame.mixer.Sound(SNORLAX_SOUND)



    def move(self, dt):
        pass

    def collide(self):
        keys = pygame.key.get_pressed()
        if self.box.colliderect(self.game.player.hitbox) and not self.game.menu_open and keys[pygame.K_SPACE] and not self.game.inEvent and not self.inEvent and self.delayAfterEvent >= AFTER_EVENT_DELAY:
            self.inEvent = True
            self.game.inEvent = True
            self.makeEvent()

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
            self.image = self.images[self.facing]
        elif self.inEvent and self.game.textComplete:
            self.inEvent = False
            self.game.inEvent = False
            self.delayAfterEvent = 0
            Snorlax.sound.play()
            self.kill()


    def makeEvent(self):
        StoryTextBox.init__text(self.text[self.currText] if self.text[self.currText].endswith(".txt") else self.text)
        self.game.buttons[TEXT_BUTTON].reset()
        self.currText = self.currText + 1 if self.currText < self.maxTalks - 1 else self.currText




class River:
    tmx = load_pygame(TMX_PATH)

    def __init__(self, screen, start_pos, save):
        self.start_pos = start_pos
        self.screen = screen
        self.save = save
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

        # Ground tiles
        for x, y, surf in River.tmx.get_layer_by_name("Ground").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=0)

        # 1warer tiles
        for x, y, surf in River.tmx.get_layer_by_name("Water").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            AnimatedSprite(pos, WATER_PATHS, groups=(self.sprite_group, self.collide), z=1)

        for x, y, surf in River.tmx.get_layer_by_name("Waterside").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group), z=2)

        for x, y, surf in River.tmx.get_layer_by_name("LowerTrees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group, self.collide), z=3)

        for x, y, surf in River.tmx.get_layer_by_name("UpperTrees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group), z=3)

        for x, y, surf in River.tmx.get_layer_by_name("Flowers").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group), z=1)

        for x, y, surf in River.tmx.get_layer_by_name("Grass").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group), z=3)

        for x, y, surf in River.tmx.get_layer_by_name("Buildings").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group, self.collide), z=3)

        for x, y, surf in River.tmx.get_layer_by_name("TallBuildings").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group), z=4)

        for x, y, surf in River.tmx.get_layer_by_name("Bridge").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group), z=1)

        # Players
        for obj in River.tmx.get_layer_by_name("Player"):
            if obj.properties["pos"] == start_pos:
                self.player = MC((obj.x + 16, obj.y), PLAYER_PATHS, self.sprite_group, self.collide, self, size=PLAYER_SIZE, z=3)

        # 1warer tiles
        for x, y, surf in River.tmx.get_layer_by_name("UnderBridge").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            AnimatedSprite(pos, WATER_PATHS, groups=(self.sprite_group), z=0)

        # Warps
        for obj in River.tmx.get_layer_by_name("Warps"):
            BaseWarp((obj.x, obj.y), obj.properties["pos"], image=pygame.image.load(WARP_PATH), groups=(self.sprite_group, self.collide), game=self, loc=LOCATION, z=1)

        # Trainers
        for obj in River.tmx.get_layer_by_name("Trainers"):
            facing = obj.properties["dir"]
            type = obj.type
            dis = obj.properties["dis"]
            if obj.name == "Snorlax":
                Snorlax((obj.x + 108, obj.y), name=obj.name, dis=dis, type=type, groups=(self.sprite_group, self.collide, self.entities), game=self, size=SNORLAX_SIZE, facing=facing, z=2)
            else:
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
        pygame.mixer.music.load(LEVEL_TWO_MUSIC_PATH)
        pygame.mixer.music.set_volume(GAME_VOLUME)
        pygame.mixer.music.play(-1, 10, 5000)
        StoryTextBox.init__text(TEXT_PATH1)
        StoryTextBox.init_images(TEXT_BOX_PATHS)
        RiverVolumeButton.init_images(VOL_BUTTON_PATHS)
        self.buttons = [RiverVolumeButton(MAX_X - 50, MAX_Y - 50, self)]
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
    game = River(screen, START_POS, save)
    nextStage = game.run()
    while True:
        nextStage = checkExit(nextStage)

