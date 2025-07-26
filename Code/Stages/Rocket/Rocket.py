import sys
import os
from pygame import SCALED
from pytmx.util_pygame import load_pygame
from Code.LevelOneStage.LevelOne import LevelOneVolumeButton
from Code.Stages.Lake.Lake import *
from Code.Entities.Trainer import *
from Code.sprites import *
from Code.Save import *
from Code.entities import *

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BLOCK_SIZE = 32
PLAYER_SIZE = (32, 64)
MAX_X, MAX_Y = 740, 493
MAX_FPS = 0
LEVEL_TWO_MUSIC_PATH = os.path.join(BASE_DIR, "../../../Audio/Rocket.mp3")
FADE_LEVEL = 100
FADE_CHANGE_PER_FRAME = 8
FADE_IN_CHANGE_PER_FRAME = 24

GAME_VOLUME = 0.3
ANIM_SPEED = 8

DELAY_AFTER_CLICK = 4
TEXT_BOX_POS = (65, MAX_Y - 140)
TEXT_BUTTON, VOLUME_BUTTON = 0, 1
TEXT_BOX_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/TextBox.png"),
                  os.path.join(BASE_DIR, "../../../Assets/UI/TextBoxArrow.png")]
VOL_BUTTON_PATHS = [os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/NoMute.png"),
                    os.path.join(BASE_DIR, "../../../Assets/UI/Buttons/Mute.png")]
DELAY_AT_START = 10
WARP_PATH = os.path.join(BASE_DIR, "../../../Assets/Background/Warp.png")
LOCATION = "rocket"
START_POS = "home"
MAX_ALPHA = 255
FINAL_DELAY = 5

# New constants for slide show
SLIDE_IMAGES = [
    os.path.join(BASE_DIR, "../../../Assets/RocketSlides/First.png"),
    os.path.join(BASE_DIR, "../../../Assets/RocketSlides/Second.png"),
    os.path.join(BASE_DIR, "../../../Assets/RocketSlides/Third.png"),
    os.path.join(BASE_DIR, "../../../Assets/RocketSlides/Fourth.png"),
]

SLIDE_TEXTS = [
    os.path.join(BASE_DIR, "First.txt"),
    os.path.join(BASE_DIR, "Second.txt"),
    os.path.join(BASE_DIR, "Third.txt"),
    os.path.join(BASE_DIR, "Fourth.txt"),
]

STAGES = {}

# Initialize pygame
pygame.init()
# screen = pygame.display.set_mode((MAX_X, MAX_Y), flags=SCALED, vsync=1) #Andre
screen = pygame.display.set_mode((MAX_X, MAX_Y)) #Rhysmond


class RocketVolumeButton(LevelOneVolumeButton):

    def first_toggle(self):
        if self.game.save.getMuted():
            pygame.mixer.music.set_volume(0 if self.playing else GAME_VOLUME)
            StoryTextBox.clickSound.set_volume(0 if self.playing else GAME_VOLUME)
            self.playing = not self.playing
            self.update_image()

    def toggle_volume(self):
        pygame.mixer.music.set_volume(0 if self.playing else GAME_VOLUME)
        StoryTextBox.clickSound.set_volume(0 if self.playing else GAME_VOLUME)
        self.game.save.updateMuted()
        self.playing = not self.playing
        self.update_image()

    def update_image(self):
        self.image_idx = 1 if not self.playing else 0


class Rocket:
    def __init__(self, screen, start_pos, save):
        self.screen = screen
        self.save = save
        self.save.updateStage(START_POS.title())
        self.save.updatePos(LOCATION)
        self.buttons = [None, None]
        self.alpha = 255  # Start fully faded out
        self.rect = self.screen.get_rect()
        self.fadeSurface = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)

        # Slide show variables
        self.current_slide = 0
        self.slide_images = []
        self.slide_texts = SLIDE_TEXTS
        self.load_slide_images()
        self.max_slides = len(self.slide_images)  # Store total number of slides

        # State variables
        self.ticker = 0
        self.textComplete = False
        self.boxFinished = False
        self.isClicked = False
        self.clickDelay = 0
        self.stageDone = False
        self.finalDelay = 0
        self.running = True

        # Transition states
        self.is_fading_out = False
        self.is_fading_in = True  # Start with fade in
        self.waiting_for_input = False
        self.transition_complete = False
        self.all_slides_complete = False

        self.inBattle = False

    def load_slide_images(self):
        """Load all slide images"""
        for path in SLIDE_IMAGES:
            img = pygame.image.load(path).convert()
            if img.get_size() != (MAX_X, MAX_Y):
                img = pygame.transform.scale(img, (MAX_X, MAX_Y))
            self.slide_images.append(img)

    def init_text_box(self):
        """Initialize the text box for current slide"""
        StoryTextBox.init_images(TEXT_BOX_PATHS)
        with open(self.slide_texts[self.current_slide], 'r') as file:
            text_lines = [line.strip() for line in file.readlines()]
        StoryTextBox.init__text(text_lines)

        # Remove existing text box if any
        self.buttons[TEXT_BUTTON] = StoryTextBox(TEXT_BOX_POS[0], TEXT_BOX_POS[1], self)

        # Reset text state
        self.textComplete = False
        self.boxFinished = False
        self.waiting_for_input = False

    def update_game_state(self, dt):
        """Update game state each frame"""
        # Initial delay before showing first slide
        if self.ticker < DELAY_AT_START:
            self.ticker = min(self.ticker + dt * ANIM_SPEED, DELAY_AT_START)
            return

        # Handle transition between slides
        if self.transition_complete:
            self.current_slide += 1
            if self.current_slide >= self.max_slides:
                self.all_slides_complete = True
                self.is_fading_out = True  # Start final fade out
                return

            self.init_text_box()
            self.is_fading_in = True
            self.transition_complete = False
            return

        # Handle final transition after all slides
        if self.all_slides_complete and not self.is_fading_out:
            self.stageDone = True
            return

        # Only process input and text when not transitioning
        if not self.is_fading_in and not self.is_fading_out and not self.all_slides_complete:
            # Check for spacebar to advance text/slide
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not self.isClicked:
                self.buttons[TEXT_BUTTON].action()
                self.clickDelay = DELAY_AFTER_CLICK
                self.isClicked = True

            # Update text animation
            for button in self.buttons:
                if isinstance(button, StoryTextBox):
                    button.updateString(dt)

            # Handle text completion
            if self.textComplete and not self.is_fading_out:
                self.is_fading_out = True
                self.waiting_for_input = False

            # Handle click delay
            if self.isClicked:
                self.clickDelay -= dt * ANIM_SPEED
                if self.clickDelay <= 0:
                    self.isClicked = False

    def fade(self, dt):
        """Handle screen fading effects"""
        if self.is_fading_in:
            # Fade in (alpha decreasing)
            self.alpha = max(self.alpha - FADE_IN_CHANGE_PER_FRAME * dt * ANIM_SPEED, 0)
            if self.alpha == 0:
                self.is_fading_in = False
                self.waiting_for_input = True

        elif self.is_fading_out:
            # Fade out (alpha increasing)
            self.alpha = min(self.alpha + FADE_IN_CHANGE_PER_FRAME * dt * ANIM_SPEED, 255)
            if self.alpha == 255:
                self.is_fading_out = False
                if not self.all_slides_complete:
                    self.transition_complete = True
                else:
                    self.stageDone = True

        # Apply current fade state
        self.fadeSurface.fill((0, 0, 0, self.alpha))
        self.screen.blit(self.fadeSurface, (0, 0))

    def redraw(self):
        """Redraw all elements on screen"""
        # Draw current slide (if not all slides complete)
        if not self.all_slides_complete:
            self.screen.blit(self.slide_images[self.current_slide], (0, 0))

        # Draw buttons (only when not fading out and not all slides complete)
        if not self.is_fading_out and not self.all_slides_complete:
            for button in self.buttons:
                if button:  # Check if button exists
                    button.draw(self.screen)

    def handle_events(self):
        """Handle all pygame events"""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            # Only handle button events when not transitioning
            if not self.is_fading_in and not self.is_fading_out:
                # Handle button events
                for button in self.buttons:
                    button.check_hover(mouse_pos)
                    if button.handle_event(event):
                        break

    def run(self):
        """Main game loop for the slide show"""
        pygame.mixer.music.load(LEVEL_TWO_MUSIC_PATH)
        pygame.mixer.music.set_volume(GAME_VOLUME)
        pygame.mixer.music.play(-1, 10, 5000)

        # Initialize first slide
        self.init_text_box()

        # Add volume button
        RocketVolumeButton.init_images(VOL_BUTTON_PATHS)
        self.buttons[VOLUME_BUTTON] = RocketVolumeButton(MAX_X - 50, MAX_Y - 50, self)
        self.buttons[VOLUME_BUTTON].first_toggle()

        clock = pygame.time.Clock()

        while self.running and not self.stageDone:
            dt = clock.tick(60) / 1000.0  # Convert to seconds

            self.handle_events()
            self.update_game_state(dt)

            # Draw everything
            self.screen.fill("black")
            self.redraw()
            self.fade(dt)

            pygame.display.flip()

        # Return next stage
        if self.stageDone:
            # Stop music before transitioning
            pygame.mixer.music.fadeout(500)
            self.save.updatePokemon({"name": "Daniel", "level": 21})
            return self.save.getStage()(self.screen, LOCATION, self.save)
        return None

def checkExit(nextStage):
    if nextStage is not None:
        return nextStage.run()
    else:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    save = Save("test")
    save.updateStage(LOCATION.title())
    SaveSystem.write(save)

    game = Rocket(screen, START_POS, save)
    nextStage = game.run()

    while True:
        nextStage = checkExit(nextStage)


