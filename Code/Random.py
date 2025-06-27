import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
ORANGE = (255, 100, 0)
YELLOW = (255, 200, 50)
WHITE = (255, 255, 255)

# Rocket size and position
ROCKET_WIDTH = 7 * 32    # 224 px
ROCKET_HEIGHT = 8 * 32   # 256 px
rocket_x = WIDTH // 2 - ROCKET_WIDTH // 2
rocket_y = HEIGHT // 2 - ROCKET_HEIGHT // 2

# Particle class
class FireParticle:
    def __init__(self, x, y):
        self.x = x + random.randint(-60, 60)
        self.y = y + random.randint(0, 20)
        self.radius = random.randint(6, 14)
        self.color = random.choice([ORANGE, YELLOW, WHITE])
        self.life = 30
        self.dy = random.uniform(2.0, 5.0)

    def update(self):
        self.y += self.dy
        self.radius = max(0, self.radius - 0.2)
        self.life -= 1

    def draw(self, surf):
        if self.life > 0 and self.radius > 0:
            s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, self.color + (140,), (self.radius, self.radius), int(self.radius))
            surf.blit(s, (self.x - self.radius, self.y - self.radius))

particles = []

# Placeholder rocket (you can use your own sprite instead)
rocket_img = pygame.Surface((ROCKET_WIDTH, ROCKET_HEIGHT), pygame.SRCALPHA)
pygame.draw.rect(rocket_img, WHITE, (0, 0, ROCKET_WIDTH, ROCKET_HEIGHT), border_radius=10)

# Game loop
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw rocket
    screen.blit(rocket_img, (rocket_x, rocket_y))

    # Fire emitter location: bottom-center of the rocket
    fire_origin_x = rocket_x + ROCKET_WIDTH // 2
    fire_origin_y = rocket_y + ROCKET_HEIGHT

    # Create new fire particles
    for _ in range(10):
        particles.append(FireParticle(fire_origin_x, fire_origin_y))

    # Update and draw fire particles
    for p in particles[:]:
        p.update()
        p.draw(screen)
        if p.life <= 0:
            particles.remove(p)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
