import sys
import os
import random
import copy

import pygame.sprite
from pytmx.util_pygame import load_pygame
from Code.Stages.Lake.Lake import *
from Code.Entities.Trainer import *
from Code.sprites import *
from Code.entities import *
from Code.Save import *
from Code.Battle import Battle

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMX_PATH = os.path.join(BASE_DIR, "../../../Data/TilemapsPNG/Crater.tmx")
START_POS = "snow"
DOWN, LEFT, RIGHT, UP = 2, 0, 1, 3
BLOCK_SIZE = 32
PLAYER_SIZE = (32, 64)
PLAYER_SPEED = BLOCK_SIZE // 2
MAX_SPEED = BLOCK_SIZE
MAX_X, MAX_Y = 740, 493
MAX_FPS = 0
LEVEL_TWO_MUSIC_PATH = os.path.join(BASE_DIR, "../../../Audio/Crater.mp3")
BATTLE_MUSIC_PATH = os.path.join(BASE_DIR, "../../../Audio/Battle/battle_song.mp3")
POKEBALL_PATH = [os.path.join(BASE_DIR, '../../../Assets/backgrounds/pokeball.png')]
FADE_LEVEL = 0
FADE_CHANGE_PER_FRAME = 12
FADE_IN_CHANGE_PER_FRAME = 36
PLAYER_PATHS = [os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkLeft.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkRight.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkFront.png'),
                os.path.join(BASE_DIR, '../../../Assets/Players/Darnielle/walkBack.png')]
INTERACTABLE_BOUNDS = [0, 0]

PINK = os.path.join(BASE_DIR, '../../../Assets/Background/Pink.png')

GAME_VOLUME = 0.2
ANIM_SPEED = 8

DELAY_AFTER_CLICK = 4
TEXT_BOX_POS = (65, MAX_Y - 140)
TEXT_BUTTON, VOLUME_BUTTON = 1, 0
TEXT_PATH1 = os.path.join(BASE_DIR, "Crater.txt")
TEXT_BOX_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/TextBox.png"),
                  os.path.join(BASE_DIR, "../../../Assets/UI/TextBoxArrow.png")]
VOL_BUTTON_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/NoMute.png"),
                    os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/Mute.png")]
DELAY_AT_START = 10
WARP_PATH = os.path.join(BASE_DIR, "../../../Assets/Background/Warp.png")
LOCATION = "crater"
MAX_ALPHA = 255
FINAL_DELAY = 5

FURINA_PATH = os.path.join(BASE_DIR, "../../../Assets/Players/Furina/StandingFurina.png")

DANIEL_ROAD = [RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT,
               UP, UP, UP, UP, UP ,UP, UP, UP, UP, UP, UP, UP, UP, UP]
DANIEL_PATHS = [os.path.join(BASE_DIR, "../../../Assets/Pokemon/DanielLeft.png"), os.path.join(BASE_DIR, "../../../Assets/Pokemon/DanielRight.png")]
STAGES = {}

BLIZZARD_PARTICLE_COUNT = 340  # Increased for better coverage
BLIZZARD_PARTICLE_SPEED = 180  # Slightly slower
BLIZZARD_PARTICLE_SIZE_RANGE = (3, 6)  # More size variation
BLIZZARD_WIND_CHANGE_INTERVAL = 5.0  # Longer between direction changes
BLIZZARD_ALPHA = 220  # Slightly more transparent

# Add these with the other effect constants
ROCKET_FIRE_PARTICLE_COUNT = 400
ROCKET_FIRE_PARTICLE_SPEED = 80  # pixels per second
ROCKET_FIRE_SPAWN_RADIUS = 100  # Smaller spawn area
ROCKET_FIRE_LIFETIME = 3
ROCKET_FIRE_COLORS = [
    (255, 100, 0),  # Orange
    (255, 50, 0),   # Darker orange
    (255, 150, 0),  # Yellow-orange
    (255, 200, 0)   # Yellow
]
ROCKET_FIRE_PARTICLE_SIZE_RANGE = (20, 40)  # Much smaller particles
LAUNCH_TEXT = os.path.join(BASE_DIR, "Launch.txt")
ROCKET_SOUND = os.path.join(BASE_DIR, "../../../Audio/Rocket.wav")


# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((MAX_X, MAX_Y))

# pokemon frames
pokemon_frames = {
    'icons': import_folder_dict(os.path.join(BASE_DIR, '../../../Assets/Pokemon/icons')),
    'pokemon': monster_importer(4, 2, os.path.join(BASE_DIR, '../../../Assets/Pokemon/pokemon')),
    'ui': import_folder_dict(os.path.join(BASE_DIR, '../../../Assets/UI/ui')),
    'attacks': attack_importer(os.path.join(BASE_DIR, '../../../Assets/attacks'))
}
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

#bg frames
bg_frames = import_folder_dict(os.path.join(BASE_DIR, '../../../Assets/backgrounds'))

class CraterVolumeButton(LakeVolumeButton):

    def first_toggle(self):
        if self.game.save.getMuted():
            pygame.mixer.music.set_volume(0 if self.playing else GAME_VOLUME)
            StoryTextBox.clickSound.set_volume(0 if self.playing else GAME_VOLUME)
            BaseWarp.warpSound.set_volume(0 if self.playing else GAME_VOLUME)
            Menu.open_sound.set_volume(0 if self.playing else GAME_VOLUME)
            Menu.click_sound.set_volume(0 if self.playing else GAME_VOLUME)
            Menu.select_sound.set_volume(0 if self.playing else GAME_VOLUME)
            Battle.select_sound.set_volume(0 if self.playing else GAME_VOLUME)
            Battle.toggle_sound.set_volume(0 if self.playing else GAME_VOLUME)
            Crater.liftoffSound.set_volume((0 if self.playing else GAME_VOLUME))
            self.playing = not self.playing
            self.update_image()

    def toggle_volume(self):
        pygame.mixer.music.set_volume(0 if self.playing else GAME_VOLUME)
        StoryTextBox.clickSound.set_volume(0 if self.playing else GAME_VOLUME)
        BaseWarp.warpSound.set_volume(0 if self.playing else GAME_VOLUME)
        Menu.open_sound.set_volume(0 if self.playing else GAME_VOLUME)
        Menu.click_sound.set_volume(0 if self.playing else GAME_VOLUME)
        Menu.select_sound.set_volume(0 if self.playing else GAME_VOLUME)
        Battle.select_sound.set_volume(0 if self.playing else GAME_VOLUME)
        Battle.toggle_sound.set_volume(0 if self.playing else GAME_VOLUME)
        Crater.liftoffSound.set_volume((0 if self.playing else GAME_VOLUME))
        self.game.save.updateMuted()
        self.playing = not self.playing
        self.update_image()

    def update_image(self):
        self.image_idx = 1 if not self.playing else 0

class RocketFireEffect:
    def __init__(self, rocket_pos):
        self.particles = []
        self.rocket_pos = rocket_pos
        # Create a surface for drawing particles with per-pixel alpha
        self.particle_surface = pygame.Surface((MAX_X, MAX_Y), pygame.SRCALPHA)

    def update(self, dt, rocket_pos):
        self.rocket_pos = rocket_pos

        # Update existing particles
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)

        # Add new particles
        for _ in range(int(ROCKET_FIRE_PARTICLE_COUNT * dt)):
            self.particles.append(RocketFireParticle(self.rocket_pos[0], self.rocket_pos[1]))

    def draw(self, surface):
        # Clear the particle surface
        self.particle_surface.fill((0, 0, 0, 0))

        # Draw all particles to the intermediate surface
        for particle in self.particles:
            particle.draw(self.particle_surface)

        # Draw debug marker at base position
        pygame.draw.circle(self.particle_surface, (255, 0, 0),
                           (int(self.rocket_pos[0]), int(self.rocket_pos[1])), 5)

        # Blit the particle surface onto the main surface
        surface.blit(self.particle_surface, (0, 0))


class RocketFireParticle:
    def __init__(self, x, y):
        # Ensure particles spawn around the given position
        self.x = x + random.uniform(-ROCKET_FIRE_SPAWN_RADIUS, ROCKET_FIRE_SPAWN_RADIUS)
        self.y = y + random.uniform(0, ROCKET_FIRE_SPAWN_RADIUS)  # Only spawn below the base
        self.size = random.uniform(*ROCKET_FIRE_PARTICLE_SIZE_RANGE)
        self.color = random.choice(ROCKET_FIRE_COLORS)
        self.speed = random.uniform(ROCKET_FIRE_PARTICLE_SPEED * 0.5, ROCKET_FIRE_PARTICLE_SPEED * 1.5)
        self.lifetime = random.uniform(ROCKET_FIRE_LIFETIME * 0.5, ROCKET_FIRE_LIFETIME * 1.5)
        self.age = 0
        self.direction = random.uniform(math.pi/2 + math.pi/8, math.pi/2 - math.pi/8)  # More upward direction
        self.alpha = 255

    def update(self, dt):
        self.age += dt
        # Move particle based on direction
        self.x += math.cos(self.direction) * self.speed * dt
        self.y += math.sin(self.direction) * self.speed * dt
        # Gravity effect
        self.y += 50 * dt
        # Fade out over lifetime
        self.alpha = 255 * (1 - (self.age / self.lifetime))

    def is_alive(self):
        return self.age < self.lifetime

    def draw(self, surface):
        alpha_color = (*self.color, min(255, int(self.alpha)))
        pygame.draw.circle(surface, alpha_color, (int(self.x) - BLOCK_SIZE * 32, int(self.y) - BLOCK_SIZE * 50), int(self.size))

# Add this class to handle blizzard particles
class BlizzardParticle:
    def __init__(self, screen_width, screen_height):
        # Distribute particles more evenly across the screen
        self.x = random.uniform(-screen_width, screen_width * 2)  # Wider spawn range
        self.y = random.uniform(-screen_height, screen_height * 2)  # Taller spawn range
        self.size = random.uniform(*BLIZZARD_PARTICLE_SIZE_RANGE)
        self.speed = random.uniform(BLIZZARD_PARTICLE_SPEED * 0.5, BLIZZARD_PARTICLE_SPEED * 1.5)
        self.alpha = random.randint(BLIZZARD_ALPHA - 50, BLIZZARD_ALPHA + 50)
        # Random starting age to prevent synchronized fading
        self.age = random.uniform(0, BLIZZARD_WIND_CHANGE_INTERVAL)

    def update(self, dt, wind_direction):
        # Move particle based on wind direction (slightly randomized)
        angle_variation = random.uniform(-0.2, 0.2)
        effective_angle = wind_direction + angle_variation
        self.wind_direction =wind_direction


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

            self.alpha = 255

    def draw(self, surface):
        color = (255, 255, 255, min(255, self.alpha))
        # Add some variation to particle shapes
        if random.random() < 0.7:  # 70% chance to be a circle
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))
        else:  # 30% chance to be a small line
            end_x = self.x + math.cos(self.wind_direction) * self.size * 1.5
            end_y = self.y + math.sin(self.wind_direction) * self.size * 1.5
            pygame.draw.line(surface, color,
                             (int(self.x), int(self.y)),
                             (int(end_x), int(end_y)),
                             max(1, int(self.size/2)))


class BlizzardEffect:
    def __init__(self, screen_width, screen_height):
        self.particles = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.wind_direction = math.pi / 4  # 45 degrees (NE direction)
        self.wind_change_timer = 0
        self.particle_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

        # Initialize particles gradually over time instead of all at once
        self.particles_to_init = BLIZZARD_PARTICLE_COUNT
        self.init_rate = 60  # Particles per second to initialize

    def update(self, dt):
        # Initialize new particles gradually
        if self.particles_to_init > 0:
            particles_to_add = min(int(self.init_rate * dt), self.particles_to_init)
            for _ in range(particles_to_add):
                self.particles.append(BlizzardParticle(self.screen_width, self.screen_height))
            self.particles_to_init -= particles_to_add

        # Occasionally change wind direction
        self.wind_change_timer += dt
        if self.wind_change_timer >= BLIZZARD_WIND_CHANGE_INTERVAL:
            self.wind_change_timer = 0
            # Smoother wind direction changes
            self.wind_direction += random.uniform(-math.pi/8, math.pi/8)
            self.wind_direction %= 2 * math.pi

        # Update all particles
        for particle in self.particles[:]:
            particle.update(dt, self.wind_direction)
            # Remove particles that are too far off-screen
            if (particle.x < -self.screen_width or particle.x > self.screen_width * 2 or
                    particle.y < -self.screen_height or particle.y > self.screen_height * 2):
                self.particles.remove(particle)
                # Add a new particle to maintain count
                if self.particles_to_init <= 0:
                    self.particles.append(BlizzardParticle(self.screen_width, self.screen_height))

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


class ToLowerLayer(BaseWarp):

    def __init__(self, pos, stage, image, groups, game, z=1):
        super().__init__(pos, stage, image, groups, game, z)

    def warp(self):
        self.game.player.collidable = self.game.collide

        for sprite in self.game.bridges:
            sprite.z = 4


class DanielCrater(Entity):
    ini = False

    def __init__(self, pos, groups, game, size, facing, name, road=DANIEL_ROAD, text=None, z=3):
        if not DanielCrater.ini:
            DanielCrater.init_assets(DANIEL_PATHS)
            DanielCrater.ini = True
        super().__init__(pos, groups, size, z)
        self.game = game
        self.facing = dirs[facing]

        self.road = [] if not road else road

        self.images = DanielCrater.assets
        self.image = self.images[self.facing]
        self.currentStep = 0
        self.maxSteps = len(self.road)
        self.box = pygame.Rect(self.x, self.y, self.rect.width + INTERACTABLE_BOUNDS[0], self.rect.height + INTERACTABLE_BOUNDS[1])
        self.box.center = (self.x, self.y)

        self.TRAINER_GO_SPEED = FURINA_GO_SPEED

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

        self.go = False

    @classmethod
    def init_assets(cls, paths):
        cls.assets = []
        for path in paths:
            image = pygame.image.load(path)
            cls.assets.append(image)

    def makeEvent(self):
        StoryTextBox.init__text(self.text if not self.go else LAUNCH_TEXT)
        self.game.buttons[TEXT_BUTTON].reset()
        self.game.save.updateEvent("Daniel")

    def collide(self):
        keys = pygame.key.get_pressed()
        if self.box.colliderect(self.game.player.hitbox) and not self.game.menu_open and keys[pygame.K_SPACE] and not self.game.inEvent and not self.inEvent and self.delayAfterEvent >= AFTER_EVENT_DELAY:
            self.inEvent = True
            self.game.inEvent = True
            self.game.player.collidable = self.game.warps
            self.makeEvent()

    def move(self, dt):
        # Store previous position
        if self.go and self.currentStep < self.maxSteps:
            down = self.road[int(self.currentStep)] == DOWN
            left = self.road[int(self.currentStep)] == LEFT
            right = self.road[int(self.currentStep)] == RIGHT
            up = self.road[int(self.currentStep)] == UP

            if left and not right:
                self.x -= dt * FURINA_GO_SPEED
                if self.facing != LEFT:
                    self.facing = LEFT

            elif right and not left:
                self.x += dt * FURINA_GO_SPEED
                if self.facing != RIGHT:
                    self.facing = RIGHT

            else:
                self.y = self.y + dt * FURINA_GO_SPEED if down else self.y - dt * FURINA_GO_SPEED

            self.currentStep += dt * ANIM_DIST

        elif self.go:
            self.makeEvent()
            if self.game.player.following == self:
                self.game.player.following = None
            self.kill()  # Remove Daniel from all groups
            self.game.endEvent = True
        else:
            pass


    def update(self, dt):
        # Update position
        self.rect.center = (self.x, self.y)
        self.hitbox.center = (self.x, self.y + PLAYER_SIZE[1] // 4)
        self.box.center = (self.x, self.y)
        if not self.inEvent and not self.game.inEvent:
            self.delayAfterEvent += 0 if self.delayAfterEvent >= AFTER_EVENT_DELAY else dt * ANIM_SPEED
        elif self.game.inEvent:
            self.delayAfterEvent = 0

        # Check for collisions
        if self.inEvent and self.game.textComplete:
            self.go = True
            # Set player to follow Daniel
            self.game.player.following = self

        # Update sprite properties
        self.move(dt)
        self.y_sort = self.rect.centery
        self.image = self.images[self.facing]


class Crater:
    tmx = load_pygame(TMX_PATH)
    liftoffSound = pygame.mixer.Sound(ROCKET_SOUND)

    def __init__(self, screen, start_pos, save):
        self.start_pos = start_pos
        self.screen = screen
        self.save = save
        self.sprite_group = AllSprites()
        self.collide = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.encounter = pygame.sprite.Group()
        self.collideUpper = pygame.sprite.Group()
        self.bridges = pygame.sprite.Group()
        self.rocket = pygame.sprite.Group()
        self.rocketFloor = pygame.sprite.Group()
        self.warps = pygame.sprite.Group()
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

        self.rocket_fire = None
        self.rocket_base_pos = None  # Will store the base position of the rocket

        self.talkedDaniel = self.save.gotDaniel()
        self.endEvent = False

        self.liftoff = False
        self.liftoff_speed = BLOCK_SIZE * 15  # Speed of liftoff
        self.liftoff_distance = MAX_Y * 5    # Distance to move upwards before ending

        self.monsters = [
            {0: Pokemon('Buneary', 12)},
            {0: Pokemon('Cindrill', 10)},
            {0: Pokemon('Draem', 12)},
            {0: Pokemon('Finsta', 9)},
            {0: Pokemon('Jacana', 13)},
            {0: Pokemon('Atrox', 11)},
        ]

        self.encounter_timer = Timer(2000, func=self.pokemon_encounter)
        self.inBattle = False

        # transition / tint
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.transition_target = None
        self.tint_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.tint_mode = 'untint'
        self.tint_progress = 0
        self.tint_direction = -1
        self.tint_speed = 600
        self.tint_type = 'fade'  # 'fade' or 'flash'
        self.flash_count = 0
        self.flash_total = 3  # 3 flashes = 6 transitions (in+out x3)
        self.flash_state = 'in'  # current phase of a flash

        self.transition_music_path = BATTLE_MUSIC_PATH
        self.transition_music_playing = False
        self.bg_music_muted = False

        # Add pokeball image loading
        self.pokeball_image = pygame.image.load(POKEBALL_PATH[0]).convert_alpha()
        self.pokeball_rect = self.pokeball_image.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.pokeball_alpha = 0
        self.show_pokeball = False

        # Add pokeball fade speed
        self.pokeball_fade_speed = 20000

        # Pokeball animation properties
        self.pokeball_scale = 1.0
        self.pokeball_target_scale = 5.0
        self.pokeball_growth_duration = 700
        self.pokeball_growth_timer = 0
        self.pokeball_growing = False
        self.pokeball_rotation = 0  # Current rotation angle (degrees)
        self.pokeball_target_rotation = 360  # Complete 1 full rotation


    def init_assets(self, start_pos):

        # Ground tiles
        for x, y, surf in Crater.tmx.get_layer_by_name("Ground").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=0)

        for x, y, surf in Crater.tmx.get_layer_by_name("Water").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=1)

        for x, y, surf in Crater.tmx.get_layer_by_name("Exit").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=1)

        # Grass tiles
        for x, y, surf in Crater.tmx.get_layer_by_name("Floor").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=self.sprite_group, z=2)

        for x, y, surf in Crater.tmx.get_layer_by_name("RocketFloor").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.rocket, self.rocketFloor), z=2)

        for x, y, surf in Crater.tmx.get_layer_by_name("Stairs").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=2)

        for x, y, surf in Crater.tmx.get_layer_by_name("MoreStairs").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=1)

        for x, y, surf in Crater.tmx.get_layer_by_name("EvenMoreStairs").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=1)

        for x, y, surf in Crater.tmx.get_layer_by_name("FinalStairs").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=1)


        for x, y, surf in Crater.tmx.get_layer_by_name("Grass").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.encounter), z=3)


        for x, y, surf in Crater.tmx.get_layer_by_name("Rock").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.collide, self.collideUpper), z=3)

        # 1warer tiles
        for x, y, surf in Crater.tmx.get_layer_by_name("Wall").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group, self.collide, self.collideUpper), z=1)

        for x, y, surf in Crater.tmx.get_layer_by_name("UpperWall").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group), z=1)

        # 1warer tiles
        for x, y, surf in Crater.tmx.get_layer_by_name("Buildings").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group, self.collide, self.collideUpper), z=3)

        # 1warer tiles
        for x, y, surf in Crater.tmx.get_layer_by_name("TallBuildings").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group), z=4)

        # 1warer tiles
        for x, y, surf in Crater.tmx.get_layer_by_name("Rocket").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group, self.collide, self.collideUpper, self.rocket), z=3)

        # 1warer tiles
        for x, y, surf in Crater.tmx.get_layer_by_name("TallRocket").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group, self.rocket), z=5)

        # 1warer tiles
        for x, y, surf in Crater.tmx.get_layer_by_name("RocketWall").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos, image=surf, groups=(self.sprite_group, self.rocket, self.collide, self.collideUpper), z=4)

        # Players
        for obj in Crater.tmx.get_layer_by_name("Player"):
            if obj.properties["pos"] == start_pos:
                self.player = MC((obj.x + 16, obj.y), PLAYER_PATHS, self.sprite_group, self.collideUpper, self, size=PLAYER_SIZE, z=3)

        for x, y, surf in Crater.tmx.get_layer_by_name("FloorWall").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.collide, self.collideUpper), z=1)

        #tree_image = pygame.image.load(TREE_PATH[0])
        for x, y, surf in Crater.tmx.get_layer_by_name("LowerTrees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            tree = Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.collide, self.collideUpper), z=3)

        for x, y, surf in Crater.tmx.get_layer_by_name("UpperTrees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=3)

        for x, y, surf in Crater.tmx.get_layer_by_name("Trunk").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=2)

        for x, y, surf in Crater.tmx.get_layer_by_name("FixTrees").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group), z=3)

        for x, y, surf in Crater.tmx.get_layer_by_name("Bridge").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.bridges), z=2)

        for x, y, surf in Crater.tmx.get_layer_by_name("BridgeWall").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=pygame.transform.scale_by(pygame.image.load(WARP_PATH), 0.5), groups=(self.sprite_group, self.collideUpper), z=4)

        for x, y, surf in Crater.tmx.get_layer_by_name("UnderBridge").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.collide), z=1)

        for x, y, surf in Crater.tmx.get_layer_by_name("FloorWall").tiles():
            pos = (x * BLOCK_SIZE, y * BLOCK_SIZE)
            Sprite(pos=pos, image=surf, groups=(self.sprite_group, self.collide, self.collideUpper), z=3)

        # Warps
        for obj in Crater.tmx.get_layer_by_name("Warps"):
            image=pygame.image.load(WARP_PATH)
            if obj.properties["size"] == "small":
                image = pygame.transform.scale_by(image, 0.5)
            elif obj.properties["size"] == "large":
                image = pygame.transform.scale_by(image, 4)
            BaseWarp((obj.x, obj.y), obj.properties["pos"], image=image, groups=(self.sprite_group, self.collide, self.collideUpper, self.warps), game=self, loc=LOCATION, z=2)

        #def __init__(self, pos, paths, group, game, size, road, z=2):
        # Trainers
        for obj in Crater.tmx.get_layer_by_name("Trainers"):
            facing = obj.properties["dir"]
            type = obj.type
            dis = obj.properties["dis"]
            if obj.name == "FurinaCrater":
                image=pygame.image.load(FURINA_PATH)
                Sprite(pos=(obj.x + 16, obj.y), image=pygame.transform.flip(image, True, False), groups=(self.sprite_group, self.collide, self.collideUpper), z=3)
            elif obj.name == "DanielCrater":
                DanielCrater((obj.x + BLOCK_SIZE * 2, obj.y + BLOCK_SIZE * 3), name=obj.name, groups=(self.sprite_group, self.collide, self.entities, self.collideUpper), game=self, size=(BLOCK_SIZE * 6, BLOCK_SIZE * 6), facing=facing, z=4)
            else:
                Trainer((obj.x + 16, obj.y), name=obj.name, dis=dis, type=type, groups=(self.sprite_group, self.collide, self.entities, self.collideUpper), game=self, size=PLAYER_SIZE, facing=facing, z=3)

        for obj in Crater.tmx.get_layer_by_name("ToLower"):
            image=pygame.image.load(WARP_PATH)
            ToLowerLayer((obj.x, obj.y), None, pygame.transform.scale_by(image, 2), (self.sprite_group, self.collideUpper), game=self, z=4)

        for obj in Crater.tmx.get_layer_by_name("ToUpper"):
            image=pygame.image.load(WARP_PATH)
            ToUpperLayer((obj.x, obj.y), None, pygame.transform.scale_by(image, 2), (self.sprite_group, self.collide), game=self, z=4)

        # In init_assets() - Update the rocket base position code
        for obj in Crater.tmx.get_layer_by_name("RocketBase"):
            if obj.properties.get("base"):
                # Calculate center position of the base tile
                self.rocket_base_pos = (obj.x + obj.width//2, obj.y + obj.height)
                self.rocket_fire = RocketFireEffect(self.rocket_base_pos)
                break

        # Pokemon menu
        self.menu = Menu(self.player.player_pokemon, fonts, pokemon_frames, self.player)
        self.menu_open = False

        # Battle
        self.battle = None

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

        # Handle liftoff sequence
        if self.endEvent and not self.liftoff and self.textComplete:
            for sprite in self.rocketFloor:
                sprite.z = 4
            self.liftoff = True
            Crater.liftoffSound.play()
            # Start liftoff music or sound effect here if desired

        if self.liftoff:
            if self.rocket_base_pos:
                self.rocket_base_pos = (self.rocket_base_pos[0],
                                        self.rocket_base_pos[1] + dt * 30)
                self.rocket_fire.update(dt, self.rocket_base_pos)

            # Move player upwards
            self.player.y -= self.liftoff_speed * dt
            self.player.rect.center = (self.player.x, self.player.y)
            self.player.hitbox.center = (self.player.x, self.player.y + PLAYER_SIZE[1] // 4)

            # Move rocket and tall rocket upwards
            for rocket in self.rocket:
                rocket.rect.y -= self.liftoff_speed * dt / 1.10

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

        # Draw rocket fire if liftoff is happening
        if self.liftoff and self.rocket_fire:
            self.rocket_fire.draw(self.screen)

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

        if self.textComplete and not self.inBattle and not self.inEvent and keys[pygame.K_RETURN] and not self.prev_keys[pygame.K_RETURN]:
            self.menu.open_sound.play()
            self.menu_open = not self.menu_open
            self.player.toggleblock()

        self.prev_keys = keys

    def check_pokemon(self):
        if [sprite for sprite in self.encounter if
            sprite.rect.colliderect(self.player.hitbox)] and not self.battle and self.player.moving:
            if not self.encounter_timer.active:
                self.encounter_timer.activate()

    def pokemon_encounter(self):
        print('lol')
        if [sprite for sprite in self.encounter if
            sprite.rect.colliderect(self.player.hitbox)] and not self.battle and self.player.moving:
            selected_monsters = random.choice(self.monsters)
            self.start_battle(copy.deepcopy(selected_monsters), None)

    def end_battle(self):
        self.inBattle = False
        self.encounter_timer.deactivate()
        self.transition_target = 'level'  # Signal we're returning to overworld
        self.tint_mode = 'tint'  # Start fading to black
        self.tint_type = 'fade'
        self.tint_progress = 0  # Reset progress

        # Reset pokeball state
        self.show_pokeball = False
        self.pokeball_alpha = 0

        # Reset music
        if self.transition_music_playing:
            pygame.mixer.music.load(LEVEL_TWO_MUSIC_PATH)
            volume = 0 if self.save.getMuted() else GAME_VOLUME
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
            self.transition_music_playing = False

        self.bg_music_muted = False
        self.player.blocked = True  # Keep player blocked during transition

    def start_battle(self, monsters, trainer):
        if self.battle is None:
            self.transition_target = Battle(
                player_pokemon=self.player.player_pokemon,
                opponent_pokemon=monsters,
                pokemon_frames=pokemon_frames,
                bg_surf=bg_frames['forest'],
                fonts=fonts,
                trainer=trainer,
                game=self
            )
            self.inBattle = True
            self.tint_mode = 'tint'
            self.tint_type = 'flash'
            self.flash_count = 0
            self.flash_total = 3
            self.flash_state = 'in'
            self.tint_progress = 0
            self.chain_fade_after_flash = True
            self.show_pokeball = False  # Start with pokeball hidden

            # Music: mute bg and play battle music
            if not self.bg_music_muted:
                pygame.mixer.music.set_volume(0)
                self.bg_music_muted = True

            if not self.transition_music_playing:
                pygame.mixer.music.load(self.transition_music_path)
                volume = 0 if self.save.getMuted() else GAME_VOLUME * 0.8
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1)
                self.transition_music_playing = True

            # block player
            self.player.blocked = True

    def tint_screen(self, dt):
        if self.tint_type == 'fade':
            if self.tint_mode == 'untint':
                self.tint_progress -= self.tint_speed * dt
                if self.show_pokeball:
                    self.pokeball_alpha -= self.pokeball_fade_speed * dt
                    self.pokeball_alpha = max(0, self.pokeball_alpha)

                # When fade out completes
                if self.tint_progress <= 0:
                    if self.transition_target == 'level':
                        # Clear battle and return to overworld
                        self.battle = None
                        self.player.blocked = False  # Now unblock player
                        self.transition_target = None
                    elif isinstance(self.transition_target, Battle):
                        # Transition to new battle
                        self.battle = self.transition_target
                        self.transition_target = None

            elif self.tint_mode == 'tint':
                self.tint_progress += self.tint_speed * dt
                if self.show_pokeball:
                    self.pokeball_alpha += self.pokeball_fade_speed * dt
                    self.pokeball_alpha = min(255, self.pokeball_alpha)

                # When screen is fully black
                if self.tint_progress >= 255:
                    if self.transition_target == 'level':
                        # SWITCH TO OVERWORLD HERE
                        self.battle = None
                        self.transition_target = None
                        self.tint_mode = 'untint'  # begin fade-in
                        self.player.blocked = False
                        self.show_pokeball = False

                    elif isinstance(self.transition_target, Battle):
                        # SWITCH TO BATTLE HERE
                        self.battle = self.transition_target
                        self.transition_target = None
                        self.tint_mode = 'untint'  # begin fade-in
                        self.show_pokeball = False

        elif self.tint_type == 'flash':
            speed = self.tint_speed * dt * 3

            if self.flash_state == 'in':
                self.tint_progress += speed
                if self.tint_progress >= 255:
                    self.tint_progress = 255
                    self.flash_state = 'out'
            elif self.flash_state == 'out':
                self.tint_progress -= speed
                if self.tint_progress <= 0:
                    self.tint_progress = 0
                    self.flash_count += 1
                    if self.flash_count >= self.flash_total:
                        # Transition to pokeball sequence
                        self.tint_type = 'pokeball'
                        self.tint_mode = 'tint'
                        self.tint_progress = 0
                        self.show_pokeball = True
                    else:
                        self.flash_state = 'in'


        elif self.tint_type == 'pokeball':
            if self.tint_mode == 'tint':
                # Step 1: Fade-in pokeball
                self.pokeball_alpha += self.pokeball_fade_speed * dt
                if self.pokeball_alpha >= 255:
                    self.pokeball_alpha = 255
                    self.tint_mode = 'grow_pokeball'
                    self.pokeball_growing = True
                    self.pokeball_growth_timer = 0
                    self.pokeball_scale = 1.0  # Start at normal size
                    self.pokeball_rotation = 0  # Reset rotation

            elif self.tint_mode == 'grow_pokeball':
                # Step 2: Grow and spin pokeball over 2 seconds
                self.pokeball_growth_timer += dt * 1000  # Convert to milliseconds
                # Calculate growth progress (0 to 1)
                growth_progress = min(1.0, self.pokeball_growth_timer / self.pokeball_growth_duration)
                # Ease-out scaling for smoother animation
                eased_progress = 1 - (1 - growth_progress) ** 2
                self.pokeball_scale = 1 + (self.pokeball_target_scale - 1) * eased_progress
                # Update rotation (complete 360 degrees over the growth duration)
                self.pokeball_rotation = growth_progress * self.pokeball_target_rotation
                # When growth completes
                if growth_progress >= 1.0:
                    self.tint_mode = 'fadeout_pokeball'
                    self.tint_progress = 0  # Reset tint for fade-to-black
                    self.pokeball_growing = False

            elif self.tint_mode == 'fadeout_pokeball':
                # Step 3: Fade screen to black over pokeball
                self.tint_progress += self.tint_speed * dt
                if self.tint_progress >= 255:
                    self.tint_progress = 255
                    self.tint_mode = 'hold_black'
                    self.pokeball_alpha = 0
                    self.black_hold_timer = 0
                    self.pokeball_scale = 1.0  # Reset scale

            elif self.tint_mode == 'hold_black':
                self.black_hold_timer += dt
                if self.black_hold_timer >= 1:
                    # Transition into battle BEFORE fade-in
                    if isinstance(self.transition_target, Battle):
                        self.battle = self.transition_target
                        self.transition_target = None
                    self.tint_type = 'fade'
                    self.tint_mode = 'untint'
                    self.tint_progress = 255  # Start fade-in from black

        # Apply the tints and overlays
        self.tint_progress = max(0, min(self.tint_progress, 255))
        self.tint_surf.set_alpha(self.tint_progress)
        self.display_surface.blit(self.tint_surf, (0, 0))

        # Modified pokeball drawing
        if self.show_pokeball and self.pokeball_alpha > 0:
            # Create scaled pokeball surface
            scaled_width = int(self.pokeball_image.get_width() * self.pokeball_scale)
            scaled_height = int(self.pokeball_image.get_height() * self.pokeball_scale)

            # Rotate the original image first (better quality than rotating scaled image)
            rotated_pokeball = pygame.transform.rotate(self.pokeball_image, -self.pokeball_rotation)

            # Then scale the rotated image
            scaled_pokeball = pygame.transform.scale(
                rotated_pokeball,
                (scaled_width, scaled_height)
            )

            # Center the scaled and rotated pokeball
            pokeball_rect = scaled_pokeball.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

            # Apply alpha and draw
            scaled_pokeball.set_alpha(self.pokeball_alpha)
            self.display_surface.blit(scaled_pokeball, pokeball_rect)

    def run(self):
        self.init_assets(self.start_pos)
        pygame.mixer.music.load(LEVEL_TWO_MUSIC_PATH)
        pygame.mixer.music.set_volume(GAME_VOLUME)
        pygame.mixer.music.play(-1, 10, 5000)
        StoryTextBox.init__text(TEXT_PATH1)
        StoryTextBox.init_images(TEXT_BOX_PATHS)
        LakeVolumeButton.init_images(VOL_BUTTON_PATHS)
        self.buttons = [CraterVolumeButton(MAX_X - 50, MAX_Y - 50, self)]
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
                self.encounter_timer.update()
                self.check_pokemon()
                self.input()
                self.sprite_group.update(dt)


            self.screen.fill("white")
            self.sprite_group.draw(self.player.rect.center)
            # Draw blizzard on top of everything except UI elements
            self.blizzard.draw(self.screen)
            self.redraw()
            if self.menu_open: self.menu.update(dt)

            if self.battle: self.battle.update(dt)

            self.buttons[VOLUME_BUTTON].draw(self.screen)

            self.fade(dt)
            self.tint_screen(dt)
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
    game = Crater(screen, START_POS, save)
    nextStage = game.run()
    while True:
        nextStage = checkExit(nextStage)



