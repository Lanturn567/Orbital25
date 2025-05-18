import pygame
import random
from LevelTwo import Entity, TEXT_BUTTON
from StoryTextBox import StoryTextBox


BLOCK_SIZE = 32
PLAYER_SIZE = (32, 64)
DOWN, LEFT, RIGHT, UP = 2, 0, 1, 3
dirs = {"left" : LEFT,
        "right" : RIGHT,
        "up" : UP,
        "down" : DOWN}
INTERACTABLE_BOUNDS = [2 * BLOCK_SIZE, 2 * BLOCK_SIZE]
TRAINER_PATHS = { "furina" : ["./Player/walkLeft.png", "./Player/walkRight.png", "./Player/walkFront.png", "./Player/walkBack.png"]
                }
ANIM_SPEED = 4
ANIM_DIST = 3
AFTER_EVENT_DELAY = 1
TRAINER_EVENT_PATH = ["Home1.txt"]


class Trainer(Entity):

    ini = False
    assets = []

    def __init__(self, pos, groups, game, size, facing, type="furina", road=None, dis=0, text=TRAINER_EVENT_PATH, z=2):
        if not Trainer.ini:
            Trainer.init_assets(TRAINER_PATHS["furina"])
            Trainer.ini = True
        super().__init__(pos, groups, size, z)
        self.game = game
        self.facing = dirs[facing]

        self.road = [] if not road else road
        if not road:
            for i in range(dis):
                self.road.append(self.facing)
            dir = self.facing + 1 if self.facing == LEFT or self.facing == DOWN else DOWN if self.facing == UP else LEFT
            for i in range(dis):
                self.road.append(dir)

        self.image = Trainer.assets[self.facing][self.currImage]
        self.currentStep = 0
        self.maxSteps = len(self.road)
        self.box = pygame.Rect(self.x, self.y, self.rect.width + INTERACTABLE_BOUNDS[0], self.rect.height + INTERACTABLE_BOUNDS[1])
        self.box.center = (self.x, self.y)

        if self.facing == LEFT:
            self.maxFrames = Trainer.leftFrames
        if self.facing == RIGHT:
            self.maxFrames = Trainer.rightFrames
        if self.facing == UP:
            self.maxFrames = Trainer.upFrames
        if self.facing == DOWN:
            self.maxFrames = Trainer.downFrames

        self.TRAINER_GO_SPEED = random.randint(2, 4) * BLOCK_SIZE

        #GO event
        self.text = text
        self.currText = 0
        self.maxTalks = len(text)
        self.ticker = 0
        self.inEvent = False
        self.delayAfterEvent = 0


    @classmethod
    def init_assets(cls, paths):
        for path in paths:
            try:
                surface = pygame.image.load(path)
            except FileNotFoundError:
                surface = pygame.Surface(PLAYER_SIZE)
                surface.fill((255, 255, 255))

            sheet_width, sheet_height = surface.get_size()
            columns = sheet_width // PLAYER_SIZE[0]
            rows = sheet_height // PLAYER_SIZE[1]

            frames = []
            for row in range(rows):
                for col in range(columns):
                    x = col * PLAYER_SIZE[0]
                    y = row * PLAYER_SIZE[1]
                    rect = pygame.Rect(x, y, PLAYER_SIZE[0], PLAYER_SIZE[1])
                    frame = surface.subsurface(rect)
                    frames.append(frame)

            cls.assets.append(frames)

        cls.leftFrames = len(cls.assets[LEFT])
        cls.rightFrames = len(cls.assets[RIGHT])
        cls.downFrames = len(cls.assets[DOWN])
        cls.upFrames = len(cls.assets[UP])


    def move(self, dt):
        # Store previous position
        if not self.inEvent:
            dir = self.road[int(self.currentStep) % self.maxSteps] if self.road else self.facing
            if not self.box.colliderect(self.game.player.hitbox) and self.maxSteps:
                if dir == LEFT:
                    self.x -= dt * self.TRAINER_GO_SPEED
                    if self.facing == LEFT:
                        self.currImage += dt * ANIM_SPEED
                    else:
                        self.facing = LEFT
                        self.currImage = 0
                        self.maxFrames = Trainer.leftFrames


                elif dir == RIGHT:
                    self.x += dt * self.TRAINER_GO_SPEED
                    if self.facing == RIGHT:
                        self.currImage += dt * ANIM_SPEED
                    else:
                        self.facing = RIGHT
                        self.currImage = 0
                        self.maxFrames = Trainer.rightFrames


                elif dir == DOWN:
                    self.y += dt * self.TRAINER_GO_SPEED
                    if self.facing == DOWN:
                        self.currImage += dt * ANIM_SPEED
                    else:
                        self.facing = DOWN
                        self.maxFrames = Trainer.downFrames
                        self.currImage = 0

                elif dir == UP:
                    self.y -= dt * self.TRAINER_GO_SPEED
                    if self.facing == UP:
                        self.currImage += dt * ANIM_SPEED
                    else:
                        self.facing = UP
                        self.currImage = 0
                        self.maxFrames = Trainer.upFrames


                self.currentStep += dt * ANIM_DIST
                self.box.center = (self.x, self.y)

            elif self.box.colliderect(self.game.player.hitbox):
                if self.game.player.x > self.x and abs(self.game.player.y - self.y) < BLOCK_SIZE // 2:
                    self.facing = RIGHT
                elif self.game.player.x < self.x and abs(self.game.player.y - self.y) < BLOCK_SIZE // 2:
                    self.facing = LEFT
                elif self.game.player.y < self.y:
                    self.facing = UP
                elif self.game.player.y >= self.y:
                    self.facing = DOWN
                self.currImage = 0


    def collide(self):
        keys = pygame.key.get_pressed()
        if self.box.colliderect(self.game.player.hitbox) and keys[pygame.K_SPACE] and not self.inEvent and self.delayAfterEvent >= AFTER_EVENT_DELAY:
            self.inEvent = True
            self.game.inEvent = True
            self.makeEvent()

    def update(self, dt):
        # Update position
        self.rect.center = (self.x, self.y)
        self.hitbox.center = (self.x, self.y + PLAYER_SIZE[1] // 4)
        self.delayAfterEvent += 0 if self.delayAfterEvent >= AFTER_EVENT_DELAY else dt * ANIM_SPEED
        # Check for collisions
        if not self.inEvent and self.game.textComplete:
            self.move(dt)
            self.y_sort = self.rect.centery
            self.image = Trainer.assets[self.facing][int(self.currImage) % self.maxFrames]
        elif self.inEvent and self.game.textComplete:
            self.inEvent = False
            self.game.inEvent = False
            self.delayAfterEvent = 0


    def makeEvent(self):
        StoryTextBox.init__text(self.text[self.currText])
        self.game.buttons[TEXT_BUTTON].reset()
        self.currText = self.currText + 1 if self.currText < self.maxTalks - 1 else self.currText



