from Code.Opening import Opening
import os
import pygame

MAX_X, MAX_Y = 740, 493
GAME_VOLUME = 0.3
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEXT_BOX_PATHS = [
    os.path.join(BASE_DIR, "..", "..", "Assets", "UI", "TextBox.png"),
    os.path.join(BASE_DIR, "..", "..", "Assets", "UI", "TextBoxArrow.png")
]
TEXT_BOX_CLICK_PATH = os.path.join(BASE_DIR, "../../Audio/TextBoxClick.wav")
TEXT_BOX_DIMENSIONS = (580, 90)
TEXT_BUTTON = 1
ARROW_DIMENSIONS = (16, 16)
FONT_SIZE = 28
CHARACTERS_PER_SECOND = 30  # Speed of text display (characters per second)
FONT_NAME = None

class StoryTextBox(Opening.Button):
    text = []
    length = 0
    madeSound = False

    @classmethod
    def init__text(cls, path):
        next = []
        #either pass in str or list
        if isinstance(path, str):
            with open(path, "r") as file:
                lines = file.readlines()
                for line in lines:
                    next.append(line.strip())
        #list
        else:
            next = path

        cls.text = next
        cls.length = len(cls.text)
        if not cls.madeSound:
            cls.clickSound = pygame.mixer.Sound(TEXT_BOX_CLICK_PATH)
            cls.clickSound.set_volume(GAME_VOLUME)
            cls.madeSound = True

    def __init__(self, x, y, game):
        super().__init__(x, y, TEXT_BOX_DIMENSIONS[0], TEXT_BOX_DIMENSIONS[1], 0, self.textBoxClick)
        self.game = game
        self.currString = ""
        self.currLine = 0
        self.currLineLength = len(StoryTextBox.text[self.currLine])
        self.currChar = 0
        self.text_padding = 30
        self.line_padding = 5
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE, italic=True, bold=True)
        self.max_line_width = TEXT_BOX_DIMENSIONS[0] - (2 * self.text_padding)
        self.wrapped_lines = []
        self.line_height = self.font.get_height()
        self.accumulated_time = 0.0  # Tracks time between character updates
        self.char_delay = 1.0 / CHARACTERS_PER_SECOND  # Time between characters

        self.name = self.game.save.getName().title()
        for i, line in enumerate(StoryTextBox.text):
            StoryTextBox.text[i] = line.replace("Darnielle", self.name)

    def wrap_text(self, text):
        """Break text into multiple lines that fit within the text box width"""
        words = text.split(' ')
        wrapped_lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = self.font.size(test_line)[0]

            if test_width <= self.max_line_width:
                current_line.append(word)
            else:
                if current_line:
                    wrapped_lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            wrapped_lines.append(' '.join(current_line))

        return wrapped_lines

    def draw(self, surface):
        box = self.images[self.image_idx]
        surface.blit(box, self.rect)

        if self.game.boxFinished:
            arrow = self.images[self.image_idx + 1]
            surface.blit(arrow, (self.rect.x + TEXT_BOX_DIMENSIONS[0] - 45,
                                 self.rect.y + TEXT_BOX_DIMENSIONS[1] - 70,
                                 ARROW_DIMENSIONS[0], ARROW_DIMENSIONS[1]))

        y_offset = self.rect.y + (TEXT_BOX_DIMENSIONS[1] - (len(self.wrapped_lines) * self.line_height)) // 2 - 5
        for line in self.wrapped_lines:
            text_surface = self.font.render(line, True, (255, 255, 255))
            surface.blit(text_surface, (self.rect.x + self.text_padding, y_offset))
            y_offset += self.line_height + self.line_padding

    def textBoxClick(self):
        def nextBox():
            self.game.isClicked = True
            self.game.boxFinished = False
            self.currString = ""
            StoryTextBox.clickSound.play()
            if self.currLine < StoryTextBox.length - 1:
                self.currLine += 1
                self.currChar = 0
                self.currLineLength = len(StoryTextBox.text[self.currLine])
                self.accumulated_time = 0.0  # Reset timer for new line
            else:
                self.game.textComplete = True

        def skipBox():
            self.game.isClicked = True
            self.currString = StoryTextBox.text[self.currLine]
            self.currChar = self.currLineLength
            self.wrapped_lines = self.wrap_text(self.currString)
            self.game.boxFinished = True

        if self.game.isClicked:
            return

        if self.game.boxFinished:
            return nextBox()
        else:
            return skipBox()

    def updateString(self, dt):
        """Update text based on delta time"""
        if self.currChar >= self.currLineLength:
            self.game.boxFinished = True
            return

        # Accumulate time since last frame
        self.accumulated_time += dt

        # Determine how many characters to add based on accumulated time
        chars_to_add = int(self.accumulated_time / self.char_delay)

        if chars_to_add > 0:
            # Add the characters
            chars_to_add = min(chars_to_add, self.currLineLength - self.currChar)
            self.currString += StoryTextBox.text[self.currLine][self.currChar:self.currChar + chars_to_add]
            self.currChar += chars_to_add
            self.wrapped_lines = self.wrap_text(self.currString)

            # Subtract the time we've accounted for
            self.accumulated_time -= chars_to_add * self.char_delay

    def reset(self):
        for i, line in enumerate(StoryTextBox.text):
            StoryTextBox.text[i] = line.replace("Darnielle", self.name)
        self.currLine = 0
        self.currChar = 0
        self.currString = ""
        self.currLineLength = len(StoryTextBox.text[self.currLine])
        self.wrapped_lines = []
        self.accumulated_time = 0.0
        self.game.boxFinished = False
        self.game.textComplete = False
