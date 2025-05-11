import pygame
import sys
import Opening
import LevelTwo

MAX_X, MAX_Y = 740, 493
BACKGROUND_FRAMES = 5
FRAME_DELAY, GAME_DELAY, FADE_DELAY = 15, 100, 2
DELAY_AFTER_CLICK = 3
BLOCKS_PER_FADE = 30
COLOR_CHANGE_PER_FADE = 15
TIMESFADE = (MAX_Y // BLOCKS_PER_FADE) + 1
CHAR_NORMAL, CHAR_FAST = 5, 20
NUMCHARS = 28
VOL_BUTTON_PATHS = ["./Buttons/NoMute.png", "./Buttons/Mute.png"]
VOL_BUTTON_DIMENSIONS = (32, 32)
INTROPATH = "./music/LevelOneIntro.mp3"
GAME_VOLUME = 0.3
TEXT_BOX_PATHS = ["TextBox.png", "TextBoxArrow.png"]
TEXT_BOX_CLICK_PATH = "./music/TextBoxClick.wav"
TEXT_PATH = "LevelOneText.txt"
TEXT_BOX_DIMENSIONS = (580, 90)
TEXT_BUTTON = 1
ARROW_DIMENSIONS = (16, 16)
ALPHA_CHANGE = 20
MAX_ALPHA = 255
FINAL_DELAY = 20


class TextBox(Opening.Button):
    text = []
    length = 0

    #initialize class before instantiate
    @classmethod
    def init__text(cls, path):
        with open(path, "r") as file:
            lines = file.readlines()
            for line in lines:
                cls.text.append(line.strip())
        cls.length = len(cls.text)
        cls.clickSound = pygame.mixer.Sound(TEXT_BOX_CLICK_PATH)
        cls.clickSound.set_volume(GAME_VOLUME)

    def __init__(self, x, y, game):
        super().__init__(x, y, TEXT_BOX_DIMENSIONS[0], TEXT_BOX_DIMENSIONS[1], 0, self.textBoxClick)
        self.game = game
        self.currString = ""
        self.currLine = 0
        self.currLineLength = len(TextBox.text[self.currLine])
        self.currChar = 0


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
        # Center of the screen

    def textBoxClick(self):
        def nextBox():
            self.game.isClicked = True
            self.game.boxFinished = False
            self.currString = ""
            TextBox.clickSound.play()
            if self.currLine < TextBox.length - 1:
                self.currLine += 1
                self.currChar = 0  # Reset character position
                self.currLineLength = len(TextBox.text[self.currLine])  # Reset line length
            else:
                self.game.textComplete = True


        def skipBox():
            self.game.isClicked = True
            self.currString = TextBox.text[self.currLine]
            self.currChar = self.currLineLength

        if self.game.isClicked:
            return

        if self.game.boxFinished:
            return nextBox()
        else:
            return skipBox()

    def updateString(self):
        if self.currChar >= self.currLineLength:
            self.game.boxFinished = True
        else:
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
        self.playing = not self.playing
        self.update_image()

    def update_image(self):
        self.image_idx = 1 if not self.playing else 0

class LevelOne:
    images = []
    songs = []

    def __init__(self, game):
        self.screen = game.screen
        self.running = True
        self.nextStage = False

        self.boxFinished = False

        self.init_assets()

        self.isClicked = False
        self.clickDelay = 0

        self.fadeCount = 0
        self.currentPNG = 0
        self.PNGdelay = 0
        self.fadeDelay = 0

        self.buttons = [LevelOneVolumeButton(MAX_X - 50, MAX_Y - 50, game),
                        TextBox(65, MAX_Y - 140, self)]

        self.textComplete = False
        self.rect = pygame.display.get_surface().get_rect()
        self.fadeOutSurface = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)
        self.alpha = 0
        self.finalDelay = 0


    def init_assets(self):
        for i in range(BACKGROUND_FRAMES):
            try:
                image = pygame.image.load("../BGL1/BgL1-" + str(i + 1) + ".png")
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


    def update_game_state(self):
        #update player
        if self.textComplete:
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not self.isClicked:
            self.buttons[TEXT_BUTTON].action()


        self.buttons[TEXT_BUTTON].updateString()
        if self.isClicked:
            self.clickDelay = (self.clickDelay + 1) % DELAY_AFTER_CLICK
            if self.clickDelay == 0:
                self.isClicked = False


    def redraw(self):
        self.screen.blit(LevelOne.images[self.currentPNG], (0, 0))
        if self.PNGdelay >= FRAME_DELAY:
            self.currentPNG = (self.currentPNG + 1) % BACKGROUND_FRAMES
            self.PNGdelay = 0
        else:
            self.PNGdelay += 1

        if self.fadeCount > TIMESFADE:
            pass
        else:
            diff = self.fadeCount * COLOR_CHANGE_PER_FADE
            colors = (max(0, 230 - diff), max(215 - diff, 0), max(0, 255 - diff))
            pygame.draw.rect(self.screen, colors, (0, 0, MAX_X, MAX_Y - BLOCKS_PER_FADE * max(0, (self.fadeCount - FADE_DELAY))), 0)
            self.fadeCount += 1

        for i, button in enumerate(self.buttons):
            if i is not TEXT_BUTTON or not self.textComplete:
                button.draw(self.screen)

        self.fadeOutSurface.fill((0, 0, 0, min(MAX_ALPHA, self.alpha)))
        self.screen.blit(self.fadeOutSurface, self.rect)
        if self.textComplete:
            self.alpha += ALPHA_CHANGE

        pygame.display.flip()

        if self.alpha >= MAX_ALPHA and self.finalDelay >= FINAL_DELAY:
            self.nextStage = True
        elif self.alpha >= MAX_ALPHA:
            self.finalDelay += 1

    def run(self):

        try:
            pygame.mixer.music.load(INTROPATH)
            pygame.mixer.music.set_volume(GAME_VOLUME)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error loading music: {e}")

        while self.running and not self.nextStage:
            pygame.time.delay(GAME_DELAY)
            self.handle_events()
            self.update_game_state()
            self.redraw()


        if not self.nextStage:
            print("Quitting...")
            pygame.quit()
            sys.exit()
        else:
            return LevelTwo.LevelTwo(self.screen)

