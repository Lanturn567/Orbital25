import sys
import os
import random
import copy
from pytmx.util_pygame import load_pygame
from Code.Stages.Lake.Lake import *
from Code.Entities.Trainer import *
from Code.sprites import *
from Code.entities import *
from Code.Save import *
from Code.Battle import Battle

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
BATTLE_MUSIC_PATH = os.path.join(BASE_DIR, "../../../Audio/Battle/battle_song.mp3")
POKEBALL_PATH = [os.path.join(BASE_DIR, '../../../Assets/backgrounds/pokeball.png')]
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


class RivalTown(Trainer):
    def __init__(self, pos, groups, game, size, facing, name, type="furina", road=[], dis=0, text=None, z=2):
        super().__init__(pos, groups, game, size, facing, name, type, road, dis, text, z)
        self.talked = self.info["talked"]
        self.talkedTo = False
        self.go = False
        self.walked = False
        self.walkAway = False
        self.first_interaction_done = False  # Track if first interaction is complete
        self.block_input = False

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
                self.game.player.blocked = False
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
                if self.game.textComplete:
                    self.game.start_battle(self.monsters, self)
                    self.block_input = True
            elif self.talkedTo:
                # After second interaction completes, walk away
                if self.defeated:
                    self.block_input = False
                    self.walkAway = True
            self.game.inEvent = False
            self.delayAfterEvent = 0

        if self.block_input and self.first_interaction_done and self.talkedTo and self.defeated and not self.inEvent and not self.game.inEvent:
            self.makeEvent(first_interaction=False)
            self.block_input = False  # Allow interaction again

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

    def collide(self):
        keys = pygame.key.get_pressed()
        if not self.block_input and self.box.colliderect(self.game.player.hitbox) and not self.game.menu_open and keys[pygame.K_SPACE] and not self.game.inEvent and not self.inEvent and not self.transitioning_to_battle and self.delayAfterEvent >= AFTER_EVENT_DELAY:
            self.inEvent = True
            self.game.inEvent = True
            self.makeEvent()
            if self.facing == UP:
                self.game.player.facing = DOWN
                self.game.player.maxFrames = MC.downFrames
            elif self.facing == DOWN:
                self.game.player.facing = UP
                self.game.player.maxFrames = MC.upFrames
            elif self.facing == RIGHT:
                self.game.player.facing = LEFT
                self.game.player.maxFrames = MC.leftFrames
            elif self.facing == LEFT:
                self.game.player.facing = RIGHT
                self.game.player.maxFrames = MC.rightFrames
            self.game.player.currImage = 0
            self.game.player.image = MC.assets[self.game.player.facing][int(self.game.player.currImage) % self.game.player.maxFrames]

            if not self.defeated and self.can_battle:
                self.awaiting_battle = True



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
        self.encounter = pygame.sprite.Group()
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
        self.monsters = [
            {0: Pokemon('Atrox', 1)},
            {0: Pokemon('Cleaf', 3)},
            {0: Pokemon('Jacana', 4)}
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
        for x, y, surf in Town.tmx.get_layer_by_name("FixTrees").tiles():
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
            if obj.properties["size"] == "small":
                image = pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE))
            if obj.properties["pos"] in ["snow"]:
                TownEventWarp((obj.x, obj.y), obj.properties["pos"], image=image, groups=(self.sprite_group, self.collide), game=self, z=2, loc=LOCATION, cond=self.save.seenElder)
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
                self.player.facing = RIGHT
                self.player.blocked = True  # Block player movement initially
            elif obj.name != "RivalTown":
                Trainer((obj.x + 16, obj.y), name=obj.name, dis=dis, type=type,
                        groups=(self.sprite_group, self.collide, self.entities),
                        game=self, size=PLAYER_SIZE, facing=facing, z=3)
        # Pokemon menu
        self.menu = Menu(self.player.player_pokemon, fonts, pokemon_frames, self.player)
        self.menu_open = False

        # Battle
        self.battle = None

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
                self.encounter_timer.update()
                self.check_pokemon()
                self.input()
                self.sprite_group.update(dt)


            self.screen.fill("black")
            self.sprite_group.draw(self.player.rect.center)
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
    game = Town(screen, START_POS, save)
    nextStage = game.run()
    while True:
        nextStage = checkExit(nextStage)

