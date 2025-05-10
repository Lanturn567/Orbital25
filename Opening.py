import pygame
import random
import sys
import ToneMatrix
import Player
import LevelOne

# Constants
MAX_X, MAX_Y = 740, 493
ASSET_SIZE = 16
COMET_PATHS = ["comet1.jpg"]
STAR_PATHS = ["star1.png"]
VOL_BUTTON_PATHS = ["NoMute.png", "Mute.png"]
MAIN_BUTTON_PATHS = ["Start.png", "Quit.png"]


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
        self.x = random.randint(40, MAX_X * 2)
        self.y = 0
        self.dx = random.randint(5, 25)
        self.dy = random.randint(5, 25)
        self.curr_img = 0

    def update_position(self):
        if self.x < -ASSET_SIZE or self.y >= MAX_Y:
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


class Comet(BGAsset):
    """Comet background assets"""
    default_color = (255, 0, 0)  # Red
    max_count = 2

    def __init__(self):
        super().__init__()
        self.dx = random.randint(10, 50)
        self.dy = random.randint(10, 50)


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

    def handle_event(self, event, game):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_clicked = True
                return False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_hovered and self.is_clicked and self.action:
                self.is_clicked = False
                self.action(game)
                return True
            self.is_clicked = False
        return False


class VolumeButton(Button):
    """Volume control button"""
    def __init__(self, x, y, opening):
        super().__init__(x, y, 32, 32, 0, self.toggle_volume)
        self.opening = opening
        self.update_image()

    def toggle_volume(self, game):
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
            self.bg = pygame.image.load('bg.jpg')
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
        self.create_buttons()
        self.title = Title()
        self.player = Player.Player()

        self.opening = True

    def initialize_assets(self):
        """Initialize all game assets"""
        Star.init_images(STAR_PATHS)
        Comet.init_images(COMET_PATHS)
        Button.init_images(MAIN_BUTTON_PATHS)
        VolumeButton.init_images(VOL_BUTTON_PATHS)
        Title.init_images()
        Player.Player.init_images()

    def create_buttons(self):
        """Create all UI buttons"""
        def start_game(game):
            print("Game started!")
            game.opening = False

        def quit_game(game):
            pygame.quit()
            sys.exit()

        self.buttons = [
            Button(MAX_X//2 - 125, MAX_Y - 300, 250, 60, 0, start_game),
            Button(MAX_X//2 - 125, MAX_Y - 210, 250, 60, 1, quit_game),
            VolumeButton(MAX_X - 50, MAX_Y - 50, self)
        ]

    def run(self):
        """Main game loop"""
        while self.running and self.opening:
            pygame.time.delay(100)
            self.handle_events()
            self.update_game_state()
            self.redraw()

        if not self.running:
            pygame.quit()
        else:
            nextStage = LevelOne.LevelOne(self)
            nextStage.run()

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
                if button.handle_event(event, self):
                    break  # If a button was clicked, don't process other buttons

    def update_game_state(self):
        """Update game objects and state"""
        # Randomly create stars and comets
        if random.randint(0, 100) < 11:
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

        #update player
        keys = pygame.key.get_pressed()
        moved = False
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

        pygame.display.flip()


if __name__ == "__main__":
    game = Opening()
    game.run()