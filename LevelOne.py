import pygame
import sys

import Opening

BG_PATH = "../BgL1.png"
MAX_X, MAX_Y = 740, 493
CHAR_NORMAL, CHAR_FAST = 5, 20
NUMCHARS = 28
BGANIMATIONFRAMES = 5
COLOR_DIFF = 5


class Text(pygame.sprite.Sprite):

    def __init__(self):
        pass

class LevelOne:

    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.nextStage = False

        self.is_clicked = False
        self.boxFinished = False
        self.displayFullBox = False
        self.startNextBox = False

        self.fadeIn = True
        try:
            self.bg = pygame.image.load(BG_PATH)
        except FileNotFoundError:
            self.bg = pygame.Surface((MAX_X, MAX_Y))
            self.bg.fill((0, 0, 0))

        self.bgAnimationFrame = -1 * BGANIMATIONFRAMES
        self.increasing = True

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

    def update_game_state(self):
        #update player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.boxFinished:
            self.startNextBox = True
        elif keys[pygame.K_SPACE] and not self.displayFullBox:
            self.displayFullBox = True

        if self.bgAnimationFrame == BGANIMATIONFRAMES and self.increasing:
            self.increasing = False
        elif self.bgAnimationFrame == 0 and not self.increasing:
            self.increasing = True
        elif self.bgAnimationFrame < BGANIMATIONFRAMES and self.increasing:
            self.bgAnimationFrame += 1
        elif self.bgAnimationFrame > -1 * BGANIMATIONFRAMES and not self.increasing:
            self.bgAnimationFrame -= 1

    def redraw(self):
        """Redraw all game elements"""
        pixels = [(0, 0), (47, 26), (142, 60), (185, 94)]

        def replace_color(surface, old_color, new_color):
            """Replaces all pixels of old_color with new_color on the given surface."""
            pixel_array = pygame.PixelArray(surface)
            pixel_array.replace(old_color, new_color)
            del pixel_array  # Unlocks the surface

        def get_tuples(surface, x, y, pos):
            old_color = surface.get_at((x, y))[:3]  # Get RGB (ignore alpha if present)
            # Ensure new_color stays within 0-255 range
            new_r = max(0, min(255, old_color[0] + COLOR_DIFF * pos))
            new_g = max(0, min(255, old_color[1] + COLOR_DIFF * pos))
            new_b = max(0, min(255, old_color[2] + COLOR_DIFF * pos))
            new_color = (new_r, new_g, new_b)
            return (old_color, new_color)

        for pixel in pixels:
            old_color, new_color = get_tuples(self.bg, pixel[0], pixel[1], self.bgAnimationFrame)
            replace_color(self.bg, old_color, new_color)

        self.screen.blit(self.bg, (0, 0))
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update_game_state()
            self.redraw()

        if not self.nextStage:
            print("Quitting...")
            pygame.quit()
            sys.exit()
        else:
            return LevelTwo.LevelTwo(self.screen)


