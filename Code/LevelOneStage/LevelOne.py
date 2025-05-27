import pygame
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Code.Opening import Opening
from Code import LevelTwoStage

MAX_X, MAX_Y = 740, 493
BACKGROUND_FRAMES = 5
BGPATHS = ["../../Assets/BGL1/BgL1-", ".png"]
FRAME_DELAY, GAME_DELAY, FADE_DELAY = 1.5, 1.0, 0.1  # Now in seconds
DELAY_AFTER_CLICK = 0.8  # Now in seconds
BLOCKS_PER_FADE = 15
COLOR_CHANGE_PER_FADE = 7
TIMESFADE = (MAX_Y // BLOCKS_PER_FADE) + 1
VOL_BUTTON_PATHS = ["../../Assets/UI/Buttons/NoMute.png", "../../Assets/UI/Buttons/Mute.png"]
VOL_BUTTON_DIMENSIONS = (32, 32)
INTROPATH = "../../Audio/LevelOneIntro.mp3"
GAME_VOLUME = 0.3
TEXT_BOX_PATHS = ["../../Assets/UI/TextBox.png", "../../Assets/UI/TextBoxArrow.png"]
TEXT_BOX_CLICK_PATH = "../../Audio/TextBoxClick.wav"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEXT_PATH = os.path.join(BASE_DIR, "LevelOneText.txt")
TEXT_BOX_DIMENSIONS = (580, 90)
TEXT_BUTTON = 1
ARROW_DIMENSIONS = (16, 16)
ALPHA_CHANGE = 100  # Alpha per second
MAX_ALPHA = 255
FINAL_DELAY = 0.5  # Now in seconds
START_POS = "begin"


class TextBox(Opening.Button):
    text = []
    length = 0
    CHARACTERS_PER_SECOND = 15  # Typing speed in characters per second

    #initialize class before instantiate
    @classmethod
    def init__text(cls, path):
        with open(path, "r") as file:
            lines = file.readlines()
            for line in lines:
                cls.text.append(line.strip())
        cls.length = len(cls.text)
        cls.clickSound = pygame.mixer.Sound(TEXT_BOX_CLICK_PATH)
        cls.clickSound.set_volume(GAME_VOLUME / 3)

    def __init__(self, x, y, game):
        super().__init__(x, y, TEXT_BOX_DIMENSIONS[0], TEXT_BOX_DIMENSIONS[1], 0, self.textBoxClick)
        self.game = game
        self.currString = ""
        self.currLine = 0
        self.currLineLength = len(TextBox.text[self.currLine])
        self.currChar = 0
        self.time_accumulator = 0.0

    #Override no enlarge and shrink on click
    def draw(self, surface):
        box = self.images[self.image_idx]
        surface.blit(box, self.rect)
        if self.game.boxFinished:
            arrow = self.images[self.image_idx + 1]
            surface.blit(arrow, (self.rect.x + TEXT_BOX_DIMENSIONS[0] - 45, self.rect.y + 20, ARROW_DIMENSIONS[0], ARROW_DIMENSIONS[1]))
        # Define a font (name, size)
        font = pygame.font.SysFont("aquakana", 20, italic=True, bold=True)
        # Render the text (text, antialias, color)
        text_surface = font.render(self.currString, True, (255, 255, 255))  # White text
        surface.blit(text_surface, text_surface.get_rect(center=(MAX_X // 2 - 15, self.rect.y + TEXT_BOX_DIMENSIONS[1] // 2)))

    def textBoxClick(self):
        def nextBox():
            self.game.isClicked = True
            self.game.boxFinished = False
            self.currString = ""
            TextBox.clickSound.play()
            if self.currLine < TextBox.length - 1:
                self.currLine += 1
                self.currChar = 0
                self.time_accumulator = 0.0
                self.currLineLength = len(TextBox.text[self.currLine])
            else:
                self.game.textComplete = True

        def skipBox():
            self.game.isClicked = True
            self.currString = TextBox.text[self.currLine]
            self.currChar = self.currLineLength
            self.time_accumulator = 0.0

        if self.game.isClicked:
            return

        if self.game.boxFinished:
            return nextBox()
        else:
            return skipBox()

    def updateString(self, dt):
        if self.currChar >= self.currLineLength:
            self.game.boxFinished = True
        else:
            self.time_accumulator += dt
            expected_chars = int(self.time_accumulator * self.CHARACTERS_PER_SECOND)

            while self.currChar < expected_chars and self.currChar < self.currLineLength:
                self.currString += TextBox.text[self.currLine][self.currChar]
                self.currChar += 1


class LevelOneVolumeButton(Opening.Button):
    """Volume control button"""
    def __init__(self, x, y, game):
        super().__init__(x, y, VOL_BUTTON_DIMENSIONS[0], VOL_BUTTON_DIMENSIONS[1], 0, self.toggle_volume)
        self.game = game
        self.playing = True
        self.update_image()

    def toggle_volume(self):
        pygame.mixer.music.set_volume(0 if self.playing else GAME_VOLUME)
        TextBox.clickSound.set_volume(0 if self.playing else GAME_VOLUME)
        self.playing = not self.playing
        self.update_image()

    def update_image(self):
        self.image_idx = 1 if not self.playing else 0

class LevelOne:
    images = []
    songs = []

    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.nextStage = False
        self.boxFinished = False
        self.init_assets()

        self.isClicked = False
        self.clickDelay = 0.0

        self.fadeCount = 0
        self.currentPNG = 0
        self.PNGdelay = 0.0
        self.fadeDelay = 0.0

        #BUTTON_POS
        self.buttons = [LevelOneVolumeButton(MAX_X - 50, MAX_Y - 50, self),
                        TextBox(65, MAX_Y - 140, self)]

        self.textComplete = False
        self.rect = pygame.display.get_surface().get_rect()
        self.fadeOutSurface = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)
        self.alpha = 0
        self.finalDelay = 0.0

    def init_assets(self):
        for i in range(BACKGROUND_FRAMES):
            try:
                image = pygame.image.load(BGPATHS[0] + str(i + 1) + BGPATHS[1])
            except FileNotFoundError:
                image = pygame.Surface((MAX_X, MAX_Y))
                image.fill((0, 0, 0))
            LevelOne.images.append(image)
        LevelOneVolumeButton.init_images(VOL_BUTTON_PATHS)
        TextBox.init_images(TEXT_BOX_PATHS)
        TextBox.init__text(TEXT_PATH)

    def handle_events(self):
        """Handle all pygame events"""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            """Handle all pygame events"""
            # Update hover state for all buttons
            for button in self.buttons:
                button.check_hover(mouse_pos)

            # Handle button events
            for button in self.buttons:
                if button.handle_event(event):
                    break  # If a button was clicked, don't process other buttons

    def update_game_state(self, dt):
        if self.textComplete:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not self.isClicked:
            self.buttons[TEXT_BUTTON].action()

        self.buttons[TEXT_BUTTON].updateString(dt)

        if self.isClicked:
            self.clickDelay += dt
            if self.clickDelay >= DELAY_AFTER_CLICK:
                self.clickDelay = 0.0
                self.isClicked = False

    def redraw(self, dt):
        self.screen.blit(LevelOne.images[self.currentPNG], (0, 0))

        self.PNGdelay += dt
        if self.PNGdelay >= FRAME_DELAY:
            self.currentPNG = (self.currentPNG + 1) % BACKGROUND_FRAMES
            self.PNGdelay = 0.0

        if self.fadeCount > TIMESFADE:
            pass
        else:
            diff = self.fadeCount * COLOR_CHANGE_PER_FADE
            colors = (max(0, 230 - diff), max(215 - diff, 0), max(0, 255 - diff))
            pygame.draw.rect(self.screen, colors, (0, 0, MAX_X, MAX_Y - BLOCKS_PER_FADE * max(0, (self.fadeCount - FADE_DELAY))), 0)
            self.fadeDelay += dt
            if self.fadeDelay >= 0.1:
                self.fadeCount += 1
                self.fadeDelay = 0.0

        for i, button in enumerate(self.buttons):
            if i is not TEXT_BUTTON or not self.textComplete:
                button.draw(self.screen)

        self.fadeOutSurface.fill((0, 0, 0, min(MAX_ALPHA, self.alpha)))
        self.screen.blit(self.fadeOutSurface, self.rect)

        if self.textComplete:
            self.alpha += ALPHA_CHANGE * dt  # Now properly scaled per second

        pygame.display.flip()

        if self.alpha >= MAX_ALPHA and self.finalDelay >= FINAL_DELAY:
            self.nextStage = True
        elif self.alpha >= MAX_ALPHA:
            self.finalDelay += dt

    def run(self):
        from Code.LevelTwoStage.LevelTwo import LevelTwo

        clock = pygame.time.Clock()

        try:
            pygame.mixer.music.load(INTROPATH)
            pygame.mixer.music.set_volume(GAME_VOLUME)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error loading Audio: {e}")

        while self.running and not self.nextStage:
            dt = clock.tick(60) / 1000.0  # Convert to seconds
            self.handle_events()
            self.update_game_state(dt)
            self.redraw(dt)

        if not self.nextStage:
            print("Quitting...")
            pygame.quit()
            sys.exit()
        else:
            return LevelTwo(self.screen, START_POS)

if __name__ == "__main__":
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((MAX_X, MAX_Y), flags=pygame.SCALED, vsync=1)
    pygame.display.set_caption("Level 1")
    game = LevelOne(screen)
    nextStage = game.run()