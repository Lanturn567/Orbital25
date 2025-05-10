import pygame
import random
import sys
import ToneMatrix

# Constants
MAX_X, MAX_Y = 740, 493
ASSET_SIZE = 16
COMET_PATHS = ["comet1.jpg"]
STAR_PATHS = ["star1.png"]
VOL_BUTTONS = ["NoMute.png", "Mute.png"]


class BGAsset:
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


class Star(BGAsset):
    images = []
    count = 0
    max_count = 6

    @classmethod
    def init_images(cls, paths):
        for path in paths:
            try:
                cls.images.append(pygame.image.load(path))
            except pygame.error:
                print(f"Image not found: {path}")
                surf = pygame.Surface((ASSET_SIZE, ASSET_SIZE))
                surf.fill((255, 255, 255))
                cls.images.append(surf)

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
            Star.count -= 1
        return success


class Comet(BGAsset):
    images = []
    count = 0
    max_count = 3

    @classmethod
    def init_images(cls, paths):
        for path in paths:
            try:
                cls.images.append(pygame.image.load(path))
            except pygame.error:
                print(f"Image not found: {path}")
                surf = pygame.Surface((ASSET_SIZE, ASSET_SIZE))
                surf.fill((255, 0, 0))
                cls.images.append(surf)

    def __init__(self):
        super().__init__()
        self.dx = random.randint(10, 50)
        self.dy = random.randint(10, 50)

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
            Comet.count -= 1
        return success


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
        self.is_hovered = False
        self.font = pygame.font.SysFont('aquakana', 24, italic=True)
        self.shadow_offset = 3
        self.click_offset = 5
        self.is_clicked = False
        self.glow_alpha = 10
        self.glow_surface = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)

    def draw(self, surface):
        # Draw glow effect when hovered
        if self.is_hovered and self.glow_alpha < 100:
            self.glow_alpha = min(self.glow_alpha + 15, 100)
        elif not self.is_hovered and self.glow_alpha > 0:
            self.glow_alpha = max(self.glow_alpha - 15, 0)

        if self.glow_alpha > 0:
            self.glow_surface.fill((0, 0, 0, 0))
            glow_color = (*self.hover_color[:3], self.glow_alpha)
            pygame.draw.rect(self.glow_surface, glow_color,
                             (10, 10, self.rect.width, self.rect.height),
                             border_radius=8)
            surface.blit(self.glow_surface, (self.rect.x-10, self.rect.y-10))

        # Calculate offset if button is being clicked
        offset = self.click_offset if self.is_clicked else 0

        # Draw main button
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color,
                         (self.rect.x + offset, self.rect.y + offset,
                          self.rect.width, self.rect.height),
                         border_radius=8)

        # Draw border
        border_color = (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255))
        pygame.draw.rect(surface, border_color,
                         (self.rect.x + offset, self.rect.y + offset,
                          self.rect.width, self.rect.height),
                         2, border_radius=8)

        # Draw text with shadow
        text_surface = self.font.render(self.text, True, (30, 30, 30))
        text_rect = text_surface.get_rect(center=(self.rect.centerx + offset + 2,
                                                  self.rect.centery + offset + 2))
        surface.blit(text_surface, text_rect)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.rect.centerx + offset,
                                                  self.rect.centery + offset))
        surface.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_clicked = True
                return False  # Wait for mouseup to trigger action

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_hovered and self.is_clicked and self.action:
                self.is_clicked = False
                self.action()
                return True
            self.is_clicked = False

        return False


class VolumeButton:
    images = []
    volX = MAX_X - 50
    volY = MAX_Y - 50
    off = False

    @classmethod
    def init_images(cls, paths):
        cls.images = []
        for path in paths:
            try:
                img = pygame.image.load(path)
                img = pygame.transform.scale(img, (32, 32))  # Scale to appropriate size
                cls.images.append(img)
            except pygame.error:
                print(f"Image not found: {path}")
                surf = pygame.Surface((32, 32))
                surf.fill((255, 255, 255))
                cls.images.append(surf)

    def __init__(self, opening):
        self.opening = opening
        self.current_img = 0
        self.rect = pygame.Rect(self.volX, self.volY, 32, 32)
        self.is_clicked = False

    def draw(self, surface):
        # Draw the current volume image
        surface.blit(self.images[self.current_img], (self.volX, self.volY))

    def check_hover(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_clicked = True
                return False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.is_clicked:
                self.is_clicked = False
                self.toggle_volume()
                return True
            self.is_clicked = False
        return False

    def toggle_volume(self):
        self.opening.muted = not self.opening.muted
        self.current_img = 1 if self.opening.muted else 0


def make_buttons(opening):
    def start_game():
        print("Game started!")

    def quit_game():
        pygame.quit()
        sys.exit()

    # Gradient colors for buttons
    start_color = (70, 180, 130)  # Greenish
    start_hover = (100, 210, 160)

    quit_color = (180, 70, 90)    # Reddish
    quit_hover = (210, 100, 120)

    buttons = [
        Button(MAX_X//2 - 125, MAX_Y//2 - 60, 250, 60, "START GAME",
               start_color, start_hover, (240, 240, 240), start_game),
        Button(MAX_X//2 - 125, MAX_Y//2 + 20, 250, 60, "QUIT",
               quit_color, quit_hover, (240, 240, 240), quit_game),
        VolumeButton(opening)
    ]
    return buttons


class Opening:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((MAX_X, MAX_Y))
        pygame.display.set_caption("First Game")
        # uncomment to make cursor invisible
        # pygame.mouse.set_visible(0)
        try:
            self.bg = pygame.image.load('bg.jpg')
        except pygame.error:
            self.bg = pygame.Surface((MAX_X, MAX_Y))
            self.bg.fill((0, 0, 30))
        self.comets = []
        self.stars = []

        self.muted = False  # Initialize muted state
        self.buttons = make_buttons(self)
        self.current_button = 0
        self.running = True
        self.first = True

        self.music = ToneMatrix.ToneMatrix()
        self.bar = 0

    def run(self):
        if self.first:
            Star.init_images(STAR_PATHS)
            Comet.init_images(COMET_PATHS)
            VolumeButton.init_images(VOL_BUTTONS)
            self.first = False

        while self.running:
            pygame.time.delay(100)
            mouse_pos = pygame.mouse.get_pos()

            if not self.muted:
                if self.bar == 0:
                    self.music.song()

                if self.bar % 2 == 0 and self.music.seq[self.bar // 2] != None:
                    self.music.seq[self.bar // 2].sound.play()

                self.bar = (self.bar + 1) % 32

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                for button in self.buttons:
                    button.handle_event(event)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.current_button = (self.current_button + 1) % len(self.buttons)
                    elif event.key == pygame.K_UP:
                        self.current_button = (self.current_button - 1) % len(self.buttons)
                    elif event.key == pygame.K_RETURN:
                        self.buttons[self.current_button].action()

            # Update button hover states
            for i, button in enumerate(self.buttons):
                if hasattr(button, 'check_hover'):
                    button.check_hover(mouse_pos)
                if i == self.current_button and hasattr(button, 'is_hovered'):
                    button.is_hovered = True

            # Randomly create stars and comets
            if random.randint(0, 100) < 11:
                star = Star.create()
                if star:
                    self.stars.append(star)

            if random.randint(0, 100) < 30:
                comet = Comet.create()
                if comet:
                    self.comets.append(comet)

            self.redraw()

        pygame.quit()

    def redraw(self):
        self.screen.blit(self.bg, (0, 0))

        # Update and draw stars
        self.stars = [star for star in self.stars if star.update(self.screen)]

        # Update and draw comets
        self.comets = [comet for comet in self.comets if comet.update(self.screen)]

        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)

        pygame.display.flip()


if __name__ == "__main__":
    game = Opening()
    game.run()
