from enum import StrEnum

import pygame
import random
import sys
import ToneMatrix
import Player


# Constants
MAX_X, MAX_Y = 740, 493
MIN_SPEED, MAX_SPEED = 10, 20
ASSET_SIZE = 96
GAME_DELAY = 100
PHASE_CHANGE_DELAY, TRANSITION_DELAY = 2, 8 * GAME_DELAY
BLOCKS_PER_FADE = 30
COLOR_CHANGE_PER_FADE = 15
TIMESFADE = (MAX_Y // BLOCKS_PER_FADE) + 1
STARTING_PHASE, LOADING_PHASE, END_PHASE, FADE_OUT = 0, 1, 2, 3
COMET_PATHS = ["./Assets/comet1.png"]
STAR_PATHS = ["./Assets/star1.png"]
VOL_BUTTON_PATHS = ["./UI/Buttons/NoMute.png", "./UI/Buttons/Mute.png"]
MAIN_BUTTON_PATHS = ["./UI/Buttons/Start.png", "./UI/Buttons/Quit.png",
                     "./UI/Buttons/NewGame.png", "./UI/Buttons/LoadGame.png",
                     "./UI/Buttons/Back.png"]


class BGAsset:
    """Base class for background assets like stars and comets"""
    images = []
    count = 0
    max_count = 0

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
        self.y = 0
        self.dx = 10
        self.dy = 12
        self.curr_img = 0

    def update_position(self):
        if self.x < -ASSET_SIZE * 3 or self.y >= MAX_Y:
            return False

        if self.y + self.dy > MAX_Y:
            self.y = MAX_Y
            self.x -= self.dx
        else:
            self.x -= self.dx
            self.y += self.dy

        self.curr_img = (self.curr_img + 1) % len(self.images)
        return True

    def render(self, screen):
        screen.blit(self.images[self.curr_img], (self.x, self.y))

    @classmethod
    def create(cls):
        if cls.count < cls.max_count:
            cls.count += 1
            return cls()
        return None

    def update(self, screen):
        self.render(screen)
        success = self.update_position()
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


class Comet(BGAsset):
    """Comet background assets"""
    default_color = (255, 0, 0)  # Red
    max_count = 1

    @classmethod
    def init_images(cls, paths):
        super().init_images(paths)
        cls.images = [pygame.transform.rotate(image, -30) for image in cls.images]
        cls.images = [pygame.transform.scale(image, (ASSET_SIZE * 3, ASSET_SIZE * 3)) for image in cls.images]


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
            cls.images.append(pygame.image.load("./Title/Title" + str(i + 1) + ".png"))

    def __init__(self):
        self.count = 0
        self.rect = pygame.Rect(MAX_X // 2 - 180, 40, 350, 150)


    def update(self, game):
        image = Title.images[self.count]
        game.blit(image, self.rect)
        self.count = (self.count + 1) % Title.numFrames


class Opening:

    """Main game opening screen"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((MAX_X, MAX_Y))
        pygame.display.set_caption("First Game")

        try:
            self.bg = pygame.image.load('Assets/bg.jpg')
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
            print("Game started!")
            self.currPhase = FADE_OUT

        def quit_game():
            pygame.quit()
            sys.exit()

        def select_phase():
            print("Select Option!")
            self.changingPhase = True

        def load_game():
            print("Loading Save...")

        def back_to_start():
            print("Going Back...")
            self.changingPhase = True

        if phase == 0:
            self.buttons = [Button(MAX_X//2 - 125, MAX_Y - 300, 250, 60, 0, select_phase),
                            Button(MAX_X//2 - 125, MAX_Y - 210, 250, 60, 1, quit_game),
                            VolumeButton(MAX_X - 50, MAX_Y - 50, self)]
        elif phase == 1:
            self.buttons = [VolumeButton(MAX_X - 50, MAX_Y - 50, self)]
        elif phase == 2:
            self.buttons = [Button(MAX_X//2 - 125, MAX_Y - 300, 250, 60, 2, start_game),
                            Button(MAX_X//2 - 125, MAX_Y - 210, 250, 60, 3, load_game),
                            Button(MAX_X//2 + 160, MAX_Y - 150, 100, 60, 4, back_to_start),
                            VolumeButton(MAX_X - 50, MAX_Y - 50, self)]

    def run(self):
        import LevelOne
        """Main game loop"""
        while self.running and self.opening:
            pygame.time.delay(GAME_DELAY)
            self.handle_events()
            self.update_game_state()
            self.redraw()

        pygame.time.delay(TRANSITION_DELAY)
        if not self.running:
            pygame.quit()
        else:
            nextStage = LevelOne.LevelOne(self.screen)
            return nextStage

    def handle_events(self):
        """Handle all pygame events"""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Update hover state for all buttons
            for button in self.buttons:
                button.check_hover(mouse_pos)

            # Handle button events
            for button in self.buttons:
                if button.handle_event(event):
                    break  # If a button was clicked, don't process other buttons

    def update_game_state(self):
        """Update game objects and state"""
        # Randomly create stars and comets
        if random.randint(0, 100) < 7:
            star = Star.create()
            if star:
                self.stars.append(star)

        if random.randint(0, 100) < 30:
            comet = Comet.create()
            if comet:
                self.comets.append(comet)

        # Play music if not muted
        if not self.muted:
            if self.bar == 0:
                self.music.song()

            if self.bar % 2 == 0 and self.music.seq[self.bar // 2] is not None:
                self.music.seq[self.bar // 2].sound.play()

            self.bar = (self.bar + 1) % 32

        # Phase changing
        if self.changingPhase and self.phaseChangeDelay >= PHASE_CHANGE_DELAY and self.currPhase == LOADING_PHASE:
            nextPhase = END_PHASE if self.prevPhase == STARTING_PHASE else STARTING_PHASE
            self.create_buttons(nextPhase)
            self.phaseChangeDelay = 0
            self.changingPhase = False
            self.currPhase = nextPhase
            self.prevPhase = nextPhase
        elif self.changingPhase:
            if self.phaseChangeDelay == 0:
                self.create_buttons(LOADING_PHASE)
            self.currPhase = LOADING_PHASE
            self.phaseChangeDelay += 1


        #update player
        keys = pygame.key.get_pressed()
        moved = False

        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.player.speed = min(self.player.speed + 1, MAX_SPEED)
        else:
            self.player.speed = max(self.player.speed - 1, MIN_SPEED)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(1)
            moved = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(2)
            moved = True
        if not moved:
            self.player.move(0)

        if (keys[pygame.K_UP] or keys[pygame.K_w]) and not self.player.jumping:
            self.player.move(3)
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and not self.player.jumping:
            self.player.move(4)

        if keys[pygame.K_SPACE] or self.player.jumping:
            self.player.jump()


    def redraw(self):
        """Redraw all game elements"""
        self.screen.blit(self.bg, (0, 0))

        # Update and draw stars
        self.stars = [star for star in self.stars if star.update(self.screen)]

        # Update and draw comets
        self.comets = [comet for comet in self.comets if comet.update(self.screen)]

        #Update Title
        self.title.update(self.screen)

        #Update player
        self.player.draw(self.screen)

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

            self.fadeCount += 1
        elif self.currPhase == FADE_OUT:
            self.fadeCount += 1


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
    while True:
        nextStage = checkExit(nextStage)

