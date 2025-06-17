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
TMX_PATH = os.path.join(BASE_DIR, "../../../Data/TilemapsPNG/Snow.tmx")
START_POS = "town"
DOWN, LEFT, RIGHT, UP = 2, 0, 1, 3
BLOCK_SIZE = 32
PLAYER_SIZE = (32, 64)
PLAYER_SPEED = BLOCK_SIZE // 2
MAX_SPEED = BLOCK_SIZE
MAX_X, MAX_Y = 740, 493
MAX_FPS = 0
LEVEL_TWO_MUSIC_PATH = os.path.join(BASE_DIR, "../../../Audio/Snow.mp3")
FADE_LEVEL = 0
FADE_CHANGE_PER_FRAME = 12
FADE_IN_CHANGE_PER_FRAME = 36
PLAYER_PATHS = [os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkLeft.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkRight.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkFront.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkBack.png')]
INTERACTABLE_BOUNDS = [BLOCK_SIZE, BLOCK_SIZE]

PINK = os.path.join(BASE_DIR, '../../../Assets/Background/Pink.png')

GAME_VOLUME = 0.3
ANIM_SPEED = 8

DELAY_AFTER_CLICK = 4
TEXT_BOX_POS = (65, MAX_Y - 140)
TEXT_BUTTON, VOLUME_BUTTON = 1, 0
TEXT_PATH1 = os.path.join(BASE_DIR, "Snow.txt")
TEXT_BOX_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/TextBox.png"),
                  os.path.join(BASE_DIR, "../../../Assets/UI/TextBoxArrow.png")]
VOL_BUTTON_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/NoMute.png"),
                    os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/Mute.png")]
DELAY_AT_START = 10
WARP_PATH = os.path.join(BASE_DIR, "../../../Assets/Background/Warp.png")
LOCATION = "snow"
MAX_ALPHA = 255
FINAL_DELAY = 5

STAGES = {}

# Add these constants near the top of your file
BLIZZARD_PARTICLE_COUNT = 800
BLIZZARD_PARTICLE_SPEED = 400  # pixels per second
BLIZZARD_PARTICLE_SIZE_RANGE = (3, 5)
BLIZZARD_WIND_CHANGE_INTERVAL = 3.0  # seconds
BLIZZARD_ALPHA = 255  # Semi-transparent particles

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((MAX_X, MAX_Y))
pygame.display.set_caption("Snow")

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

# Add this class to handle blizzard particles
class BlizzardParticle:
    def __init__(self, screen_width, screen_height):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(-screen_height, 0)
        self.size = random.uniform(*BLIZZARD_PARTICLE_SIZE_RANGE)
        self.speed = random.uniform(BLIZZARD_PARTICLE_SPEED * 0.5, BLIZZARD_PARTICLE_SPEED * 1.5)
        self.alpha = random.randint(BLIZZARD_ALPHA - 50, BLIZZARD_ALPHA + 50)

    def update(self, dt, wind_direction):
        # Move particle based on wind direction (slightly randomized)
        angle_variation = random.uniform(-0.2, 0.2)
        effective_angle = wind_direction + angle_variation

        self.x += math.cos(effective_angle) * self.speed * dt
        self.y += math.sin(effective_angle) * self.speed * dt

        # Wrap around screen edges
        if self.x > MAX_X:
            self.x = 0
        elif self.x < 0:
            self.x = MAX_X

        if self.y > MAX_Y:
            self.y = 0
        elif self.y < 0:
            self.y = MAX_Y

    def draw(self, surface):
        color = (255, 255, 255, min(255, self.alpha))
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))

class BlizzardEffect:
    def __init__(self, screen_width, screen_height):
        self.particles = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.wind_direction = math.pi / 4  # 45 degrees (NE direction)
        self.wind_change_timer = 0

        # Create initial particles
        for _ in range(BLIZZARD_PARTICLE_COUNT):
            self.particles.append(BlizzardParticle(screen_width, screen_height))

        # Create a surface for drawing particles with per-pixel alpha
        self.particle_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

    def update(self, dt):
        # Occasionally change wind direction
        self.wind_change_timer += dt
        if self.wind_change_timer >= BLIZZARD_WIND_CHANGE_INTERVAL:
            self.wind_change_timer = 0
            # Change wind direction by up to 45 degrees in either direction
            self.wind_direction += random.uniform(-math.pi/4, math.pi/4)
            # Keep angle between 0 and 2pi
            self.wind_direction %= 2 * math.pi

        # Update all particles
        for particle in self.particles:
            particle.update(dt, self.wind_direction)

    def draw(self, surface):
        # Clear the particle surface
        self.particle_surface.fill((0, 0, 0, 0))

        # Draw all particles to the intermediate surface
        for particle in self.particles:
            particle.draw(self.particle_surface)

        # Blit the particle surface onto the main surface
        surface.blit(self.particle_surface, (0, 0))


class ToUpperLayer(BaseWarp):

    def __init__(self, pos, stage, image, groups, game, z=1):
        super().__init__(pos, stage, image, groups, game, z)

    def warp(self):
        self.game.player.collidable = self.game.collideUpper

        for sprite in self.game.bridges:
            sprite.z = 2

        for sprite in self.game.lowerTrees:
            sprite.z = 1

        for sprite in self.game.upperTrees:
            sprite.z = 1

        for sprite in self.game.trunks:
            sprite.z = 0


class ToLowerLayer(BaseWarp):

    def __init__(self, pos, stage, image, groups, game, z=1):
        super().__init__(pos, stage, image, groups, game, z)

    def warp(self):
        self.game.player.collidable = self.game.collide

        for sprite in self.game.bridges:
            sprite.z = 4

        for sprite in self.game.lowerTrees:
            sprite.z = 3

        for sprite in self.game.upperTrees:
            sprite.z = 3

        for sprite in self.game.trunks:
            sprite.z = 2



class Snow:
    tmx = load_pygame(TMX_PATH)

    def __init__(self, screen, start_pos, save):
        self.start_pos = start_pos
        self.screen = screen
        self.save = save
        self.sprite_group = AllSprites()
        self.collide = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.bridges = pygame.sprite.Group()
        self.lowerTrees = pygame.sprite.Group()
        self.upperTrees = pygame.sprite.Group()
        self.trunks = pygame.sprite.Group()
        self.collideUpper = pygame.sprite.Group()
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

        self.blizzard = BlizzardEffect(MAX_X, MAX_Y)


    def init_assets(self, start_pos):

        # Ground tiles
        for x, y, surf in Snow.tmx.get_layer_by_name("Ground").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=0)

        # 1warer tiles
        for x, y, surf in Snow.tmx.get_layer_by_name("Wall").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group, self.collide), z=1)

        # 1warer tiles
        for x, y, surf in Snow.tmx.get_layer_by_name("UpperWall").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group, self.collideUpper), z=1)

        # Players
        #if player is on bridge, change layer to 5 else 3
        for obj in Snow.tmx.get_layer_by_name("Player"):
            if obj.properties["pos"] == start_pos:
                self.player = MC((obj.x + 16, obj.y), PLAYER_PATHS, self.sprite_group, self.collide, self, size=PLAYER_SIZE, z=3)

        # Grass tiles
        for x, y, surf in Snow.tmx.get_layer_by_name("Floor").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=2)

        #tree_image = pygame.image.load(TREE_PATH[0])
        for x, y, surf in Snow.tmx.get_layer_by_name("LowerTrees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            tree = Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.collide, self.lowerTrees), z=3)

        for x, y, surf in Snow.tmx.get_layer_by_name("UpperTrees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.upperTrees), z=3)

        for x, y, surf in Snow.tmx.get_layer_by_name("Trunk").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.trunks), z=2)

        for x, y, surf in Snow.tmx.get_layer_by_name("Bridge").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.bridges), z=4)

        for x, y, surf in Snow.tmx.get_layer_by_name("BridgeWall").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=pygame.transform.scale_by(pygame.image.load(WARP_PATH), 0.5), groups=(self.sprite_group, self.collideUpper), z=4)

        for x, y, surf in Snow.tmx.get_layer_by_name("FloorWall").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.collideUpper, self.collide), z=3)

        # Warps
        for obj in Snow.tmx.get_layer_by_name("Warps"):
            BaseWarp((obj.x, obj.y), obj.properties["pos"], image=pygame.image.load(WARP_PATH), groups=(self.sprite_group, self.collide), game=self, loc=LOCATION, z=2)

        #def __init__(self, pos, paths, group, game, size, road, z=2):
        # Trainers
        for obj in Snow.tmx.get_layer_by_name("Trainers"):
            facing = obj.properties["dir"]
            type = obj.type
            dis = obj.properties["dis"]
            Trainer((obj.x + 16, obj.y), name=obj.name, dis=dis, type=type, groups=(self.sprite_group, self.collide, self.entities, self.collideUpper), game=self, size=PLAYER_SIZE, facing=facing, z=3)

        for obj in Snow.tmx.get_layer_by_name("IncreaseZ"):
            image = pygame.image.load(WARP_PATH)
            ToUpperLayer((obj.x, obj.y), None, pygame.transform.scale_by(image, 2), (self.sprite_group, self.collide), game=self, z=4)

        for obj in Snow.tmx.get_layer_by_name("LowerZ"):
            image = pygame.image.load(WARP_PATH)
            ToLowerLayer((obj.x, obj.y), None, pygame.transform.scale_by(image, 2), (self.sprite_group, self.collideUpper), game=self, z=4)

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

        self.blizzard.update(dt)

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


            self.screen.fill("white")
            self.sprite_group.draw(self.player.rect.center)
            # Draw blizzard on top of everything except UI elements
            self.blizzard.draw(self.screen)
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
    game = Snow(screen, START_POS, save)
    nextStage = game.run()
    while True:
        nextStage = checkExit(nextStage)



