import pygame
import random
import sys
import os
from Code.Opening import ToneMatrix
from Assets import Players
import Audio
from Code.Entities import Player
from Code.Save import *

# Constants
MAX_X, MAX_Y = 740, 493
MIN_SPEED, MAX_SPEED = 10, 20
MAX_FPS = 60
ANIM_SPEED = 8
ASSET_SIZE = 96
GAME_DELAY = 100
PHASE_CHANGE_DELAY, TRANSITION_DELAY = 2, 8 * GAME_DELAY
BLOCKS_PER_FADE = 4
COLOR_CHANGE_PER_FADE = 3
TIMESFADE = (MAX_Y // BLOCKS_PER_FADE) + 1
# Add to your constants section
STARTING_PHASE, LOADING_PHASE, END_PHASE, SAVE_SELECT_PHASE, FADE_OUT, NAME_SELECT_PHASE, CONFIRM_NAME_PHASE = 0, 1, 2, 3, 4, 5, 6
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMET_PATHS = [os.path.join(BASE_DIR, "../../Assets/Opening/comet1.png")]
STAR_PATHS = [os.path.join(BASE_DIR, "../../Assets/Opening/star1.png")]
VOL_BUTTON_PATHS = [os.path.join(BASE_DIR, "../../Assets/UI/Buttons/NoMute.png"), os.path.join(BASE_DIR, "../../Assets/UI/Buttons/Mute.png")]
MAIN_BUTTON_PATHS = [os.path.join(BASE_DIR, "../../Assets/UI/Buttons/Start.png"), os.path.join(BASE_DIR, "../../Assets/UI/Buttons/Quit.png"),
                     os.path.join(BASE_DIR, "../../Assets/UI/Buttons/NewGame.png"), os.path.join(BASE_DIR, "../../Assets/UI/Buttons/LoadGame.png"),
                     os.path.join(BASE_DIR, "../../Assets/UI/Buttons/Back.png"), os.path.join(BASE_DIR, "../../Assets/UI/Buttons/Yes.png"),
                     os.path.join(BASE_DIR, "../../Assets/UI/Buttons/No.png")]
SAVE_FILE_BUTTON_PATHS = [os.path.join(BASE_DIR, "../../Assets/UI/Buttons/SaveFileButton.png")]
FONT_NAME = None
FONT_SIZE = 24

class BGAsset:
    """Base class for background assets like stars and comets"""
    images = []
    count = 0
    max_count = 0
    length = 0

    @classmethod
    def init_images(cls, paths):
        cls.images = []
        for path in paths:
            try:
                img = pygame.image.load(path)
                cls.images.append(img)
            except pygame.error:
                print(f"Image not found: {path}")
                surf = pygame.Surface((ASSET_SIZE, ASSET_SIZE))
                surf.fill(cls.default_color)
                cls.images.append(surf)

    def __init__(self):
        self.x = random.randint(40, MAX_X * 3 // 2)
        self.y = -25
        self.dx = 10
        self.dy = 12
        self.curr_img = 0

    def update_position(self, dt):
        if self.x < -ASSET_SIZE * 3 or self.y >= MAX_Y:
            return False

        if self.y + self.dy > MAX_Y:
            self.y = MAX_Y
            self.x -= self.dx * dt * ANIM_SPEED
        else:
            self.x -= self.dx * dt * ANIM_SPEED
        self.y += self.dy * dt * ANIM_SPEED

        self.curr_img += dt * ANIM_SPEED
        return True

    def render(self, screen):
        screen.blit(self.images[int(self.curr_img) % self.__class__.length], (self.x, self.y))

    @classmethod
    def create(cls):
        if cls.count < cls.max_count:
            cls.count += 1
            return cls()
        return None

    def update(self, screen, dt):
        self.render(screen)
        success = self.update_position(dt)
        if not success:
            self.__class__.count -= 1
        return success


class Star(BGAsset):
    """Star background assets"""
    default_color = (255, 255, 255)  # White
    max_count = 6

    @classmethod
    def init_images(cls, paths):
        super().init_images(paths)
        cls.images = [pygame.transform.rotate(image, 14) for image in cls.images]
        cls.length = len(cls.images)


class Comet(BGAsset):
    """Comet background assets"""
    default_color = (255, 0, 0)  # Red
    max_count = 1

    @classmethod
    def init_images(cls, paths):
        super().init_images(paths)
        cls.images = [pygame.transform.rotate(image, -30) for image in cls.images]
        cls.images = [pygame.transform.scale(image, (ASSET_SIZE * 3, ASSET_SIZE * 3)) for image in cls.images]
        cls.length = len(cls.images)

    def __init__(self):
        super().__init__()
        self.x = MAX_X + 25
        self.y = -25
        self.dx = random.randint(1, 2)
        self.dy = 0.3


class Button:
    """Base button class"""
    images = []
    scale = 1.1

    @classmethod
    def init_images(cls, paths):
        cls.images = []
        for path in paths:
            try:
                img = pygame.image.load(path)
                cls.images.append(img)
            except pygame.error:
                print(f"Image not found: {path}")
                surf = pygame.Surface((100, 50))  # Default button size
                surf.fill((200, 200, 200))
                cls.images.append(surf)

    def __init__(self, x, y, width, height, image_idx, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.is_hovered = False
        self.is_clicked = False
        self.image_idx = image_idx

    def draw(self, surface):
        image = self.images[self.image_idx]
        scale_factor = 1.0

        if self.is_hovered:
            scale_factor = self.scale  # Slightly enlarge on hover
            if self.is_clicked:
                scale_factor = 0.95  # Slightly shrink when clicked

        scaled_width = int(self.rect.width * scale_factor)
        scaled_height = int(self.rect.height * scale_factor)
        scaled_image = pygame.transform.scale(image, (scaled_width, scaled_height))

        # Center the scaled image over the button's position
        offset_x = (scaled_width - self.rect.width) // 2
        offset_y = (scaled_height - self.rect.height) // 2
        surface.blit(scaled_image, (self.rect.x - offset_x, self.rect.y - offset_y))


    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_clicked = True
                return False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_hovered and self.is_clicked and self.action:
                self.is_clicked = False
                self.action()
                return True
            self.is_clicked = False
        return False


class SaveFileButton(Button):
    color = (255, 255, 255)
    """Button representing a save file with hover/click animations, using images as base"""
    def __init__(self, x, y, width, height, save_data, action=None):
        super().__init__(x, y, width, height, 0, action)
        self.original_image = pygame.image.load(SAVE_FILE_BUTTON_PATHS[0]).convert_alpha()
        # Scale image to desired size
        self.original_image = pygame.transform.scale(self.original_image, (width, height))
        self.image = self.original_image.copy()
        self.save_data = save_data
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE, italic=True, bold=True)
        self.original_rect = pygame.Rect(x, y, width, height)
        self.current_rect = pygame.Rect(x, y, width, height)
        self.text_padding = 16  # Padding in pixels from edges
        self.line_spacing = 22  # Space between text lines

    def draw(self, surface):
        # Calculate scale factor based on hover/click state
        scale_factor = 1.0
        if self.is_hovered:
            self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE + 4, italic=True, bold=True)
            scale_factor = self.scale  # Slightly enlarge on hover
            if self.is_clicked:
                self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE - 2, italic=True, bold=True)
                scale_factor = 0.95  # Slightly shrink when clicked
        else:
            self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE, italic=True, bold=True)

        # Calculate new dimensions
        new_width = int(self.original_rect.width * scale_factor)
        new_height = int(self.original_rect.height * scale_factor)

        # Update current rect (centered on original position)
        self.current_rect.width = new_width
        self.current_rect.height = new_height
        self.current_rect.center = self.original_rect.center

        # Scale the image
        self.image = pygame.transform.scale(self.original_image, (new_width, new_height))

        # Draw the button image
        surface.blit(self.image, self.current_rect)

        # Calculate scaled padding
        scaled_padding_x = self.text_padding * (new_width / self.original_rect.width)
        scaled_padding_y = self.text_padding * (new_height / self.original_rect.height)
        scaled_line_spacing = self.line_spacing * (new_height / self.original_rect.height)

        # Draw save file info
        if self.save_data:
            # Left side text (name and stage)
            name_text = self.font.render(f"Save: {self.save_data.getName()}", True, SaveFileButton.color)
            stage_text = self.font.render(f"Stage: {self.save_data.getStageName()}", True, SaveFileButton.color)

            # Right side text (badges and pokedex)
            badges_text = self.font.render(f"Badges: {self.save_data.getBadges()}", True, SaveFileButton.color)
            pokemon_text = self.font.render(f"Pokedex: {self.save_data.getSeen()}", True, SaveFileButton.color)

            # Calculate positions for left side text
            left_text_x = self.current_rect.x + scaled_padding_x
            name_y = self.current_rect.y + scaled_padding_y
            stage_y = name_y + scaled_line_spacing

            # Calculate positions for right side text
            right_text_x = self.current_rect.right - scaled_padding_x - max(badges_text.get_width(), pokemon_text.get_width()) - 10
            badges_y = name_y
            pokemon_y = stage_y

            # Draw all text elements
            surface.blit(name_text, (left_text_x, name_y))
            surface.blit(stage_text, (left_text_x, stage_y))
            surface.blit(badges_text, (right_text_x, badges_y))
            surface.blit(pokemon_text, (right_text_x, pokemon_y))
        else:
            # Empty slot text (centered)
            empty_text = self.font.render("Empty Slot", True, SaveFileButton.color)
            text_x = self.current_rect.centerx - empty_text.get_width() // 2
            text_y = self.current_rect.centery - empty_text.get_height() // 2
            # Ensure text stays within padded area
            text_x = max(self.current_rect.x + scaled_padding_x,
                         min(text_x, self.current_rect.right - scaled_padding_x - empty_text.get_width()))
            text_y = max(self.current_rect.y + scaled_padding_y,
                         min(text_y, self.current_rect.bottom - scaled_padding_y - empty_text.get_height()))
            surface.blit(empty_text, (text_x, text_y))

    # Rest of the methods remain the same...
    def check_hover(self, mouse_pos):
        self.is_hovered = self.current_rect.collidepoint(mouse_pos)
        return self.is_hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.current_rect.collidepoint(event.pos):
                self.is_clicked = True
                return False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_clicked and self.current_rect.collidepoint(event.pos) and self.action:
                self.is_clicked = False
                self.action()
                return True
            self.is_clicked = False
        return False

class VolumeButton(Button):
    """Volume control button"""
    def __init__(self, x, y, opening):
        super().__init__(x, y, 32, 32, 0, self.toggle_volume)
        self.opening = opening
        self.update_image()

    def toggle_volume(self):
        self.opening.muted = not self.opening.muted
        self.update_image()

    def update_image(self):
        self.image_idx = 1 if self.opening.muted else 0

class Title:
    images = []
    numFrames = 6

    @classmethod
    def init_images(cls):
        for i in range(Title.numFrames):
            cls.images.append(pygame.image.load(os.path.join(BASE_DIR, "../../Assets/Title/Title" + str(i + 1) + ".png")))

    def __init__(self):
        self.count = 0
        self.rect = pygame.Rect(MAX_X // 2 - 180, 40, 350, 150)


    def update(self, game, dt):
        image = Title.images[int(self.count) % Title.numFrames]
        game.blit(image, self.rect)
        self.count += dt * ANIM_SPEED


class Opening:

    """Main game opening screen"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((MAX_X, MAX_Y))
        pygame.display.set_caption("First Game")

        try:
            self.bg = pygame.image.load(os.path.join(BASE_DIR, '../../Assets/Opening/bg.jpg'))
        except pygame.error:
            self.bg = pygame.Surface((MAX_X, MAX_Y))
            self.bg.fill((0, 0, 30))

        self.comets = []
        self.stars = []
        self.muted = False
        self.buttons = []
        self.running = True
        self.music = ToneMatrix.ToneMatrix()
        self.bar = 0
        self.lastNote = -1

        self.initialize_assets()
        self.create_buttons(STARTING_PHASE)
        self.title = Title()
        self.player = Player.OpeningPlayer()

        self.opening = True
        self.currPhase = STARTING_PHASE
        self.prevPhase = STARTING_PHASE
        self.changingPhase = False
        self.phaseChangeDelay = 0

        self.fadeCount = 0
        self.save = None

        self.action_in_progress = False

        self.key_repeat_delay = 0.4  # Initial delay before repeat starts (seconds)
        self.key_repeat_interval = 0.1  # Repeat rate (seconds)
        self.key_repeat_timers = {}  # Dictionary to track key repeat timers
        self.last_key_event_time = 0  # Time of last key event

        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_interval = 0.5  # seconds

        self.confirm_name = False
        self.confirm_buttons = []


    def initialize_assets(self):
        """Initialize all game assets"""
        Star.init_images(STAR_PATHS)
        Comet.init_images(COMET_PATHS)
        Button.init_images(MAIN_BUTTON_PATHS)
        VolumeButton.init_images(VOL_BUTTON_PATHS)
        Title.init_images()
        Player.OpeningPlayer.init_images()

    def create_buttons(self, phase):
        """Create all UI buttons"""
        def start_game():
            if self.action_in_progress:
                return
            print("Starting new game...")
            self.action_in_progress = True
            self.changingPhase = True
            self.next_phase = NAME_SELECT_PHASE

        def quit_game():
            if self.action_in_progress:
                return
            print("Quitting...")
            self.action_in_progress = True
            pygame.quit()
            sys.exit()

        def select_phase():
            if self.action_in_progress:
                return
            print("Select Option!")
            self.action_in_progress = True
            self.changingPhase = True

        def load_game():
            if self.action_in_progress:
                return
            print("Loading Save...")
            self.action_in_progress = True
            self.changingPhase = True
            self.next_phase = SAVE_SELECT_PHASE

        def back_to_start():
            if self.action_in_progress:
                return
            print("Going Back...")
            self.action_in_progress = True
            self.changingPhase = True
            if self.currPhase == SAVE_SELECT_PHASE:
                self.next_phase = END_PHASE
            elif self.currPhase == NAME_SELECT_PHASE:
                self.next_phase = END_PHASE
            elif self.currPhase == CONFIRM_NAME_PHASE:
                self.next_phase = NAME_SELECT_PHASE
            else:
                self.next_phase = STARTING_PHASE

        def load_selected_save(save):
            if self.action_in_progress:
                return
            print(f"Loading {save.getName()}...")
            self.action_in_progress = True
            self.save = save
            if not self.muted:
                self.save.setMute(False)
            else:
                self.save.setMute(True)
            SaveSystem.write(self.save)
            self.currPhase = FADE_OUT

        def confirm_save():
            if self.action_in_progress:
                return
            self.action_in_progress = True
            self.save = Save(self.player_name)
            if not self.muted:
                self.save.setMute(False)
            else:
                self.save.setMute(True)
            SaveSystem.write(self.save)
            self.currPhase = FADE_OUT

        def return_to_name_edit():
            if self.action_in_progress:
                return
            self.action_in_progress = True
            self.changingPhase = True
            self.next_phase = NAME_SELECT_PHASE
            self.confirm_name = False
            self.action_in_progress = False

        if phase == STARTING_PHASE:
            self.buttons = [
                Button(MAX_X//2 - 125, MAX_Y - 300, 250, 60, 0, select_phase),
                Button(MAX_X//2 - 125, MAX_Y - 210, 250, 60, 1, quit_game),
                VolumeButton(MAX_X - 50, MAX_Y - 50, self)
            ]
        elif phase == LOADING_PHASE:
            self.buttons = [VolumeButton(MAX_X - 50, MAX_Y - 50, self)]
        elif phase == END_PHASE:
            self.buttons = [
                Button(MAX_X//2 - 125, MAX_Y - 300, 250, 60, 2, start_game),
                Button(MAX_X//2 - 125, MAX_Y - 210, 250, 60, 3, load_game),
                Button(MAX_X//2 + 180, MAX_Y - 130, 100, 60, 4, back_to_start),
                VolumeButton(MAX_X - 50, MAX_Y - 50, self)
            ]
        elif phase == SAVE_SELECT_PHASE:
            # Get all save files from the Saves directory
            save_files = SaveSystem.list_saves()
            self.buttons = []

            # Create buttons for each save file (up to 3 slots)
            save_objects = []

            for i in range(min(len(save_files), 3)):
                currName = save_files[i]
                currSave = SaveSystem.read(currName.removesuffix(".txt"))
                save_objects.append(currSave)

                btn = SaveFileButton(MAX_X//2 - 180, MAX_Y - 300 + i * 80, 360 ,70, currSave, lambda s=currSave: load_selected_save(s))
                self.buttons.append(btn)

            while len(self.buttons) < 3:
                self.buttons.append(SaveFileButton(MAX_X//2 - 180, MAX_Y - 300 + len(self.buttons) * 80,360,70, None, lambda : print("There's no save file here!")))
            self.buttons.append(Button(MAX_X//2 + 180, MAX_Y - 130, 100, 60, 4, back_to_start))
            self.buttons.append(VolumeButton(MAX_X - 50, MAX_Y - 50, self))

        elif phase == NAME_SELECT_PHASE:
            self.player_name = ""  # Reset name when entering this phase
            self.buttons = [
                Button(MAX_X//2 + 180, MAX_Y - 130, 100, 60, 4, back_to_start),
                VolumeButton(MAX_X - 50, MAX_Y - 50, self)
            ]
        elif phase == CONFIRM_NAME_PHASE:
            self.buttons = [
                Button(MAX_X//2 - 175, MAX_Y - 125, 113, 90, 5, confirm_save),
                Button(MAX_X//2 + 60, MAX_Y - 125, 113, 90, 6, return_to_name_edit),
                VolumeButton(MAX_X - 50, MAX_Y - 50, self)
            ]

    def handle_name_input(self, event):
        current_time = pygame.time.get_ticks() / 1000
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
                self.key_repeat_timers.clear()
                self.last_key_event_time = current_time
            elif event.key == pygame.K_RETURN and len(self.player_name) > 0:
                # Transition to confirmation phase instead of immediately creating save
                self.changingPhase = True
                self.next_phase = CONFIRM_NAME_PHASE
                self.confirm_name = True
                self.action_in_progress = False
            elif event.unicode.isprintable() and len(self.player_name) < 12:
                self.key_repeat_timers[event.key] = {
                    'last_time': current_time,
                    'delay': self.key_repeat_delay,
                    'unicode': event.unicode
                }
                self.player_name += event.unicode
                self.last_key_event_time = current_time
        elif event.type == pygame.KEYUP:
            if event.key in self.key_repeat_timers:
                del self.key_repeat_timers[event.key]

    def handle_continuous_input(self, dt):
        current_time = pygame.time.get_ticks() / 1000
        keys = pygame.key.get_pressed()

        # Handle backspace repeat
        if keys[pygame.K_BACKSPACE]:
            if pygame.K_BACKSPACE not in self.key_repeat_timers:
                # First press - start timer
                self.key_repeat_timers[pygame.K_BACKSPACE] = {
                    'last_time': current_time,
                    'delay': self.key_repeat_delay
                }
                self.last_key_event_time = current_time
            else:
                # Check if it's time to repeat
                timer = self.key_repeat_timers[pygame.K_BACKSPACE]
                if current_time - timer['last_time'] >= timer['delay']:
                    self.player_name = self.player_name[:-1]
                    timer['last_time'] = current_time
                    timer['delay'] = self.key_repeat_interval  # Switch to faster repeat rate
                    self.last_key_event_time = current_time

        # Handle other key repeats
        for key, timer in list(self.key_repeat_timers.items()):
            if key == pygame.K_BACKSPACE:
                continue  # Already handled above

            if keys[key]:  # Key is still being held down
                if current_time - timer['last_time'] >= timer['delay']:
                    if len(self.player_name) < 12:
                        self.player_name += timer['unicode']
                        timer['last_time'] = current_time
                        timer['delay'] = self.key_repeat_interval  # Switch to faster repeat rate
                        self.last_key_event_time = current_time
            else:  # Key was released
                del self.key_repeat_timers[key]

    def run(self):
        from Code.LevelOneStage.LevelOne import LevelOne
        """Main game loop"""
        self.clock = pygame.time.Clock()
        while self.running and self.opening:
            dt = self.clock.tick(MAX_FPS) / 1000
            self.handle_events()
            self.update_game_state(dt)
            self.redraw(dt)

        if not self.running:
            pygame.quit()
        else:
            nextStage = self.save.getStage()(self.screen, self.save.getPos(), self.save)
            return nextStage

    def handle_events(self):
        """Handle all pygame events"""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.action_in_progress or self.changingPhase:
                    return  # Skip event handling during transitions

            if self.currPhase == NAME_SELECT_PHASE:
                self.handle_name_input(event)

            # Update hover state for all buttons
            for button in self.buttons:
                button.check_hover(mouse_pos)

            # Handle button events
            for button in self.buttons:
                if button.handle_event(event):
                    break  # If a button was clicked, don't process other buttons

    def update_game_state(self, dt):
        """Update game objects and state"""
        # Randomly create stars and comets
        if random.randint(0, 100) < 7 * dt:
            star = Star.create()
            if star:
                self.stars.append(star)

        if random.randint(0, 100) < 30 * dt:
            comet = Comet.create()
            if comet:
                self.comets.append(comet)

        # Play Audio if not muted
        if not self.muted:
            if self.bar == 0:
                self.music.song()

            if self.music.seq[int(self.bar)] is not None and int(self.bar) > self.lastNote:
                self.music.seq[int(self.bar)].sound.play()
                self.lastNote += 1

            self.bar = self.bar + dt * 4 if self.bar + dt * 4 < 16 else 0
            self.lastNote = -1 if self.bar == 0 else self.lastNote

                # Phase changing
        if self.changingPhase:
            if self.currPhase == LOADING_PHASE:
                self.phaseChangeDelay += dt * ANIM_SPEED
                if self.phaseChangeDelay >= 2.0:
                    nextPhase = getattr(self, 'next_phase', END_PHASE if self.prevPhase == STARTING_PHASE else STARTING_PHASE)
                    self.create_buttons(nextPhase)
                    self.phaseChangeDelay = 0
                    self.changingPhase = False
                    self.prevPhase = self.currPhase  # Update previous phase
                    self.currPhase = nextPhase
                    self.action_in_progress = False
                    if hasattr(self, 'next_phase'):
                        del self.next_phase
            else:
                # Transition to loading phase
                self.create_buttons(LOADING_PHASE)
                self.prevPhase = self.currPhase  # Update previous phase
                self.currPhase = LOADING_PHASE
                self.phaseChangeDelay = 0

        if self.currPhase is not NAME_SELECT_PHASE:
            #update player
            keys = pygame.key.get_pressed()
            moved = False

            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.player.speed = min(self.player.speed + 1, MAX_SPEED)
            else:
                self.player.speed = max(self.player.speed - 1, MIN_SPEED)

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.move(1, dt)
                moved = True
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.move(2, dt)
                moved = True
            if not moved:
                self.player.move(0, dt)

            if (keys[pygame.K_UP] or keys[pygame.K_w]) and not self.player.jumping:
                self.player.move(3, dt)
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and not self.player.jumping:
                self.player.move(4, dt)

            if keys[pygame.K_SPACE] or self.player.jumping:
                self.player.jump(dt)

        else:
            self.handle_continuous_input(dt)
            self.player.move(0, dt)
            if self.player.jumping:
                self.player.jump(dt)

            # Update cursor blink
            self.cursor_timer += dt
            if self.cursor_timer >= self.cursor_blink_interval:
                self.cursor_timer = 0
                self.cursor_visible = not self.cursor_visible


    def redraw(self, dt):
        """Redraw all game elements"""
        self.screen.blit(self.bg, (0, 0))

        # Update and draw stars
        self.stars = [star for star in self.stars if star.update(self.screen, dt)]

        # Update and draw comets
        self.comets = [comet for comet in self.comets if comet.update(self.screen, dt)]

        #Update Title
        self.title.update(self.screen, dt)

        #Update player
        self.player.draw(self.screen)

        # Draw title for save select phase
        if self.currPhase == SAVE_SELECT_PHASE:
            title_text = pygame.font.SysFont(FONT_NAME, 36, italic=True, bold=True).render("Select Save File", True, (255, 255, 255))
            self.screen.blit(title_text, (MAX_X//2 - title_text.get_width()//2, 165))

        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)

        if self.currPhase == FADE_OUT and self.fadeCount > TIMESFADE:
            # Create a surface with per-pixel alpha
            fade_surface = pygame.Surface((MAX_X, BLOCKS_PER_FADE * self.fadeCount), pygame.SRCALPHA)

            # Calculate the color with alpha if needed (example assumes RGB, modify if you want alpha)
            diff = self.fadeCount * COLOR_CHANGE_PER_FADE
            colors = (max(0, 230 - diff), max(215 - diff, 0), max(0, 255 - diff))

            # Draw on the surface
            pygame.draw.rect(fade_surface, colors, (0, 0, MAX_X, BLOCKS_PER_FADE * self.fadeCount), 0)

            # Blit the surface to the screen
            self.screen.blit(fade_surface, (0, 0))

            self.fadeCount += 1
            self.opening = False

        elif self.currPhase == FADE_OUT and self.fadeCount >= PHASE_CHANGE_DELAY:
            # Create a surface with per-pixel alpha
            fade_surface = pygame.Surface((MAX_X, BLOCKS_PER_FADE * self.fadeCount), pygame.SRCALPHA)

            # Calculate the color with alpha if needed (example assumes RGB, modify if you want alpha)
            diff = self.fadeCount * COLOR_CHANGE_PER_FADE
            colors = (max(0, 230 - diff), max(215 - diff, 0), max(0, 255 - diff))

            # Draw on the surface
            pygame.draw.rect(fade_surface, colors, (0, 0, MAX_X, BLOCKS_PER_FADE * (self.fadeCount - PHASE_CHANGE_DELAY)), 0)

            # Blit the surface to the screen
            self.screen.blit(fade_surface, (0, 0))
            self.fadeCount += dt * TIMESFADE * BLOCKS_PER_FADE * 0.2

        elif self.currPhase == FADE_OUT:
            self.fadeCount += dt * TIMESFADE * BLOCKS_PER_FADE * 0.2

        # Draw name selection interface
        elif self.currPhase == NAME_SELECT_PHASE:
            # Draw title
            title_text = pygame.font.SysFont(FONT_NAME, 36, italic=True, bold=True).render("Enter Your Name", True, (255, 255, 255))
            self.screen.blit(title_text, (MAX_X//2 - title_text.get_width()//2, 190))

            # Create a temporary SaveFileButton for the background
            input_bg = pygame.image.load(SAVE_FILE_BUTTON_PATHS[0])
            scaled_bg = pygame.transform.scale_by(input_bg, 1.6)
            self.screen.blit(scaled_bg, ((MAX_X - scaled_bg.get_width()) // 2, 230))

            # Draw current name (centered in the box)
            name_text = pygame.font.SysFont(FONT_NAME, 40, italic=True, bold=True).render(self.player_name, True, (255, 255, 255))
            text_x = MAX_X//2 - name_text.get_width()//2
            text_y = 240 + (80 - name_text.get_height())//2
            self.screen.blit(name_text, (text_x, text_y))

            # Draw cursor if visible
            if self.cursor_visible and len(self.player_name) < 12:
                cursor_x = text_x + name_text.get_width() + 1
                cursor_rect = pygame.Rect(cursor_x, text_y - 2, 3, name_text.get_height())
                pygame.draw.rect(self.screen, (255, 255, 255), cursor_rect)

            # Draw instructions
            instr_text = pygame.font.SysFont(FONT_NAME, 30, italic=True, bold=True).render("Press Enter to confirm", True, (255, 255, 255))
            self.screen.blit(instr_text, (MAX_X//2 - instr_text.get_width()//2, 350))

        elif self.currPhase == CONFIRM_NAME_PHASE:
            # Draw title
            title_text = pygame.font.SysFont(FONT_NAME, 36, italic=True, bold=True).render("Confirm Your Name", True, (255, 255, 255))
            self.screen.blit(title_text, (MAX_X//2 - title_text.get_width()//2, 190))

            # Create a temporary SaveFileButton for the background
            input_bg = pygame.image.load(SAVE_FILE_BUTTON_PATHS[0])
            scaled_bg = pygame.transform.scale_by(input_bg, 1.6)
            self.screen.blit(scaled_bg, ((MAX_X - scaled_bg.get_width()) // 2, 230))

            name_text = pygame.font.SysFont(FONT_NAME, 40, italic=True, bold=True).render(self.player_name, True, (255, 255, 255))
            text_x = MAX_X//2 - name_text.get_width()//2
            text_y = 240 + (80 - name_text.get_height())//2
            self.screen.blit(name_text, (text_x, text_y))

            # Draw confirmation prompt
            prompt_text = pygame.font.SysFont(FONT_NAME, 30, italic=True, bold=True).render("Is this name correct?", True, (255, 255, 255))
            self.screen.blit(prompt_text, (MAX_X//2 - prompt_text.get_width()//2, 345))

        pygame.display.flip()

def checkExit(nextStage):
    if nextStage is not None:
        return nextStage.run()
    else:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Opening()
    nextStage = game.run()
    #call save function, pass in stage, set stage.
    while True:
        nextStage = checkExit(nextStage)
        #same here

