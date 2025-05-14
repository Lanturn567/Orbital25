import Opening
import pygame

MAX_X, MAX_Y = 740, 493
GAME_VOLUME = 0.3
TEXT_BOX_PATHS = ["./UI/TextBox.png", "./UI/TextBoxArrow.png"]
TEXT_BOX_CLICK_PATH = "./music/TextBoxClick.wav"
TEXT_BOX_DIMENSIONS = (580, 90)
TEXT_BUTTON = 1
ARROW_DIMENSIONS = (16, 16)
FONT_SIZE = 20

class StoryTextBox(Opening.Button):
    text = []
    length = 0

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
        self.currLineLength = len(StoryTextBox.text[self.currLine])
        self.currChar = 0
        self.text_padding = 30
        self.line_padding = 5 # Space between wrapped lines
        self.font = pygame.font.SysFont("aquakana", FONT_SIZE, italic=True, bold=True)
        self.max_line_width = TEXT_BOX_DIMENSIONS[0] - (2 * self.text_padding)  # Available width for text
        self.wrapped_lines = []  # Stores the wrapped lines of current text
        self.line_height = self.font.get_height()  # Height of each text line


    def wrap_text(self, text):
        """Break text into multiple lines that fit within the text box width"""
        words = text.split(' ')
        wrapped_lines = []
        current_line = []

        for word in words:
            # Test if adding the word would exceed the width
            test_line = ' '.join(current_line + [word])
            test_width = self.font.size(test_line)[0]

            if test_width <= self.max_line_width:
                current_line.append(word)
            else:
                if current_line:  # If current line has content, add it
                    wrapped_lines.append(' '.join(current_line))
                current_line = [word]  # Start new line with current word

        if current_line:  # Add the last line
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

        # Draw each wrapped line
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
            else:
                self.game.textComplete = True

        def skipBox():
            self.game.isClicked = True
            self.currString = StoryTextBox.text[self.currLine]
            self.currChar = self.currLineLength
            self.wrapped_lines = self.wrap_text(self.currString)

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
            self.currString += StoryTextBox.text[self.currLine][self.currChar]
            self.currChar += 1
            self.wrapped_lines = self.wrap_text(self.currString)