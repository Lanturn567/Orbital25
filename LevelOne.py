import pygame
import sys
import Opening

MAX_X, MAX_Y = 740, 493
BACKGROUND_FRAMES = 5
FRAME_DELAY, GAME_DELAY, FADE_DELAY = 15, 100, 2
BLOCKS_PER_FADE = 30
COLOR_CHANGE_PER_FADE = 15
TIMESFADE = (MAX_Y // BLOCKS_PER_FADE) + 1
CHAR_NORMAL, CHAR_FAST = 5, 20
NUMCHARS = 28
VOL_BUTTON_PATHS = ["./Buttons/NoMute.png", "./Buttons/Mute.png"]
INTROPATH = "./music/LevelOneIntro.mp3"

class LevelOneVolumeButton(Opening.Button):
    """Volume control button"""
    def __init__(self, x, y, game):
        super().__init__(x, y, 32, 32, 0, self.toggle_volume)
        self.game = game
        self.playing = True
        self.update_image()

    def toggle_volume(self):
        pygame.mixer.music.set_volume(0 if self.playing else 1)
        self.playing = not self.playing
        self.update_image()

    def update_image(self):
        self.image_idx = 1 if not self.playing else 0

class Text(pygame.sprite.Sprite):

    def __init__(self):
        pass

class LevelOne:
    images = []
    songs = []

    def __init__(self, game):
        self.screen = game.screen
        self.running = True
        self.nextStage = False

        self.is_clicked = False
        self.boxFinished = False
        self.displayFullBox = False
        self.startNextBox = False

        self.init_assets()

        self.fadeCount = 0
        self.currentPNG = 0
        self.PNGdelay = 0
        self.fadeDelay = 0

        self.buttons = [LevelOneVolumeButton(MAX_X - 50, MAX_Y - 50, game)]  #vol button is 3 in OPENING.py


    def init_assets(self):
        for i in range(BACKGROUND_FRAMES):
            try:
                image = pygame.image.load("../BGL1/BgL1-" + str(i + 1) + ".png")
            except FileNotFoundError:
                image = pygame.Surface((MAX_X, MAX_Y))
                image.fill((0, 0, 0))
            LevelOne.images.append(image)
        LevelOneVolumeButton.init_images(VOL_BUTTON_PATHS)


    def handle_events(self):
        """Handle all pygame events"""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.is_clicked = True

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_clicked and self.boxFinished:
                    self.startNextBox = True
                elif self.is_clicked:
                    self.displayFullBox = True

            """Handle all pygame events"""
            mouse_pos = pygame.mouse.get_pos()

            # Update hover state for all buttons
            for button in self.buttons:
                button.check_hover(mouse_pos)

            # Handle button events
            for button in self.buttons:
                if button.handle_event(event):
                    break  # If a button was clicked, don't process other buttons


    def update_game_state(self):
        #update player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.boxFinished:
            self.startNextBox = True
        elif keys[pygame.K_SPACE] and not self.displayFullBox:
            self.displayFullBox = True


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

        for button in self.buttons:
            button.draw(self.screen)
        pygame.display.flip()

    def run(self):

        try:
            pygame.mixer.music.load(INTROPATH)
            pygame.mixer.music.set_volume(0.3)  # Set initial volume to max
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error loading music: {e}")

        while self.running:
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


