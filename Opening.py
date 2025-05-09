import pygame
import random
import sys
import ToneMatrix

# Constants
MAX_X, MAX_Y = 740, 493
ASSET_SIZE = 16
COMET_PATHS = ["comet1.jpg"]
STAR_PATHS = ["star1.png"]

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
        self.font = pygame.font.SysFont('Arial', 24, bold=True)
        self.shadow_offset = 3
        self.click_offset = 1
        self.is_clicked = False
        self.glow_alpha = 0
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

def make_buttons():
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
               quit_color, quit_hover, (240, 240, 240), quit_game)
    ]
    return buttons

class Opening:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((MAX_X, MAX_Y))
        pygame.display.set_caption("First Game")
        pygame.mouse.set_visible(0)
        try:
            self.bg = pygame.image.load('bg.jpg')
        except pygame.error:
            self.bg = pygame.Surface((MAX_X, MAX_Y))
            self.bg.fill((0, 0, 30))
        self.comets = []
        self.stars = []

        self.buttons = make_buttons()
        self.current_button = 0
        self.running = True
        self.first = True

        self.music = ToneMatrix.ToneMatrix()
        self.bar = 0



    def run(self):
        if self.first:
            Star.init_images(STAR_PATHS)
            Comet.init_images(COMET_PATHS)
            self.first = False
            self.music.song()

        while self.running:
            pygame.time.delay(100)
            mouse_pos = pygame.mouse.get_pos()

            if self.bar == 0:
                self.music.song()

            for note in self.music.notes[self.bar]:
                if note.play:
                    note.sound.play()

            self.bar = (self.bar + 1) % 16

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
                button.check_hover(mouse_pos)
                if i == self.current_button:
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