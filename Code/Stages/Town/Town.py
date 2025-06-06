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
TMX_PATH = os.path.join(BASE_DIR, "../../../Data/TilemapsPNG/Town.tmx")
START_POS = "right"
DOWN, LEFT, RIGHT, UP = 2, 0, 1, 3
BLOCK_SIZE = 32
PLAYER_SIZE = (32, 64)
PLAYER_SPEED = BLOCK_SIZE // 3
MAX_SPEED = BLOCK_SIZE // 3 * 2
MAX_X, MAX_Y = 740, 493
MAX_FPS = 0
LEVEL_TWO_MUSIC_PATH = os.path.join(BASE_DIR, "../../../Audio/Town.mp3")
FADE_LEVEL = 0
FADE_CHANGE_PER_FRAME = 12
FADE_IN_CHANGE_PER_FRAME = 36
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
TEXT_PATH1 = os.path.join(BASE_DIR, "Town.txt")
TEXT_BOX_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/TextBox.png"),
                  os.path.join(BASE_DIR, "../../../Assets/UI/TextBoxArrow.png")]
VOL_BUTTON_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/NoMute.png"),
                    os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/Mute.png")]
DELAY_AT_START = 10
WARP_PATH = os.path.join(BASE_DIR, "../../../Assets/Background/Warp.png")
LOST_TEXT = os.path.join(BASE_DIR, "Blizzarding.txt")
LOCATION = "town"
MAX_ALPHA = 255
FINAL_DELAY = 5

FURINA_GO_SPEED = BLOCK_SIZE * 4  # Speed for rival walking towards player
FURINA_AWAY_SPEED = BLOCK_SIZE * 4  # Speed for rival walking away

STAGES = {}

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((MAX_X, MAX_Y))
pygame.display.set_caption("Town")

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


class RivalTown(Trainer):
    def __init__(self, pos, groups, game, size, facing, name, type="furina", road=[], dis=0, text=None, z=2):
        super().__init__(pos, groups, game, size, facing, name, type, road, dis, text, z)
        self.talked = self.info["talked"]
        self.talkedTo = False
        self.go = False
        self.walked = False
        self.walkAway = False
        self.first_interaction_done = False  # Track if first interaction is complete

    def move(self, dt):
        if self.go and not self.walked:
            self.game.inEvent = True
            if self.rect.centery > self.game.player.rect.centery:
                self.facing = UP
                self.y = self.y - dt * FURINA_GO_SPEED
                self.currImage += dt * ANIM_SPEED
            elif self.rect.centerx > self.game.player.rect.centerx + BLOCK_SIZE:
                self.x -= dt * FURINA_GO_SPEED
                if self.facing == LEFT:
                    self.currImage += dt * ANIM_SPEED
                else:
                    self.facing = LEFT
                    self.currImage = 0
            else:
                self.walked = True
            self.box.center = (self.x, self.y)

        elif self.go and not self.first_interaction_done:
            self.currImage = 0
            self.makeEvent(first_interaction=True)

        elif self.walkAway:
            self.game.inEvent = True
            if self.rect.centerx < self.game.player.rect.centerx + BLOCK_SIZE * 15:
                if self.facing == RIGHT:
                    self.currImage += dt * ANIM_SPEED
                else:
                    self.facing = RIGHT
                    self.currImage = 0
                self.x += dt * FURINA_AWAY_SPEED
            else:
                self.kill()
                self.game.save.updateEvent("RivalTown")
                self.game.inEvent = False

    def update(self, dt):
        self.rect.center = (self.x, self.y)
        self.hitbox.center = (self.x, self.y + PLAYER_SIZE[1] // 4)

        if not self.inEvent and not self.game.inEvent:
            self.delayAfterEvent += 0 if self.delayAfterEvent >= AFTER_EVENT_DELAY else dt * ANIM_SPEED
        elif self.game.inEvent:
            self.delayAfterEvent = 0

        if not self.inEvent and self.game.textComplete:
            self.move(dt)
            self.y_sort = self.rect.centery
            self.image = self.images[self.facing][int(self.currImage) % self.maxFrames]
        elif self.inEvent and self.game.textComplete:
            self.inEvent = False
            if not self.first_interaction_done:
                # After first interaction completes, prepare second interaction
                self.first_interaction_done = True
                self.talkedTo = True
            elif self.talkedTo:
                # After second interaction completes, walk away
                self.walkAway = True
            self.game.inEvent = False
            self.delayAfterEvent = 0

    def makeEvent(self, first_interaction=False):
        if first_interaction:
            text_to_show = self.text
        else:
            text_to_show = self.talked

        StoryTextBox.init__text(text_to_show)
        self.game.buttons[TEXT_BUTTON].reset()
        self.inEvent = True
        self.game.inEvent = True
        self.road = []
        self.maxSteps = 0


class TownEventWarp(EventWarp):

    def __init__(self, pos, stage, image, groups, game, loc, cond, z=1):
        super().__init__(pos, stage, image, groups, game, loc, cond, z)

    def makeEvent(self):
        StoryTextBox.init__text(LOST_TEXT)
        self.game.buttons[TEXT_BUTTON].reset()
        self.game.player.x = self.rect.x
        self.game.inEvent = True
        self.afterEvent()

    def afterEvent(self):
        def checker():
            if self.game.textComplete:
                self.game.inEvent = False
                self.game.updateEvent = None
                self.game.player.x = self.rect.x - BLOCK_SIZE
                self.game.player.facing = LEFT

        self.game.updateEvent = checker


class Town:
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

        self.rival = None


    def init_assets(self, start_pos):

        # Ground tiles
        for x, y, surf in Town.tmx.get_layer_by_name("Ground").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=0)

        # 1warer tiles
        for x, y, surf in Town.tmx.get_layer_by_name("Floor").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group), z=1)

        # Island tiles
        for x, y, surf in Town.tmx.get_layer_by_name("Wall").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group, self.collide), z=2)

        #Trees tiles
        for x, y, surf in Town.tmx.get_layer_by_name("LowerTrees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group, self.collide), z=3)

        # 1warer tiles
        for x, y, surf in Town.tmx.get_layer_by_name("UpperTrees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group), z=3)

        # 1warer tiles
        for x, y, surf in Town.tmx.get_layer_by_name("Flowers").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group), z=1)

        # 1warer tiles
        for x, y, surf in Town.tmx.get_layer_by_name("Trunk").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group), z=2)

        # 1warer tiles
        for x, y, surf in Town.tmx.get_layer_by_name("Buildings").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group, self.collide), z=3)

        # 1warer tiles
        for x, y, surf in Town.tmx.get_layer_by_name("TallBuildings").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group), z=4)

        # 1warer tiles
        for x, y, surf in Town.tmx.get_layer_by_name("TallerBuildings").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group), z=4)

        # Players
        for obj in Town.tmx.get_layer_by_name("Player"):
            if obj.properties["pos"] == start_pos:
                self.player = MC((obj.x + 16, obj.y), PLAYER_PATHS, self.sprite_group, self.collide, self, size=PLAYER_SIZE, z=3)

        # Warps
        for obj in Town.tmx.get_layer_by_name("Warps"):
            image=pygame.image.load(WARP_PATH)
            if obj.properties["pos"] in ["snow"]:
                TownEventWarp((obj.x, obj.y), obj.properties["pos"], image=image, groups=(self.sprite_group, self.collide), game=self, z=2, loc=LOCATION, cond=self.save.beatGymOne)
            else:
                BaseWarp((obj.x, obj.y), obj.properties["pos"], image=image, groups=(self.sprite_group, self.collide), game=self, loc=LOCATION, z=1)

        for obj in Town.tmx.get_layer_by_name("Trainers"):
            facing = obj.properties["dir"]
            type = obj.type
            dis = obj.properties["dis"]
            if obj.name == "RivalTown" and not self.save.foughtRivalAtTown():
                self.rival = RivalTown((obj.x + 16, obj.y), name=obj.name, dis=dis, type=type,
                                       groups=(self.sprite_group, self.collide, self.entities),
                                       game=self, size=PLAYER_SIZE, facing=facing, z=3)
            elif obj.name != "RivalTown":
                Trainer((obj.x + 16, obj.y), name=obj.name, dis=dis, type=type,
                        groups=(self.sprite_group, self.collide, self.entities),
                        game=self, size=PLAYER_SIZE, facing=facing, z=3)
        # Pokemon menu
        self.menu = Menu(self.player.player_pokemon, fonts, pokemon_frames)
        self.menu_open = False

    # In the Town class
    def after_initial_text(self):
        if self.rival and not hasattr(self, 'rival_moved') and self.textComplete:
            self.rival.go = True
            self.rival_moved = True

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
            self.after_initial_text()  # Add this line
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
    game = Town(screen, START_POS, save)
    nextStage = game.run()
    while True:
        nextStage = checkExit(nextStage)

