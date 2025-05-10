import pygame

MAX_X, MAX_Y = 740, 493

class Player:
    images = []
    numFrames = 3
    playerWidth = 64
    playerHeight = 64
    playerSpeed = 10
    jumpFrames = 10
    faceForward = 14
    yboundary = 100

    @classmethod
    def init_images(cls):
        cls.images.append([pygame.image.load("./Player/standing.png")])

        left = []
        for i in range(cls.numFrames):
            left.append(pygame.image.load("./Player/L" + str(i + 1) + ".png"))
        cls.images.append(left)

        right = []
        for i in range(cls.numFrames):
            right.append(pygame.image.load("./Player/R" + str(i + 1) + ".png"))
        cls.images.append(right)

    def __init__(self):
        self.x = MAX_X // 2
        self.y = MAX_Y - Player.playerHeight - 10
        self.walkCount = 0
        self.jumpCount = Player.jumpFrames
        self.facing = 0 # 1 left, 0 forward, 2 right
        self.jumping = False
        self.speed = Player.playerSpeed
        self.stop = 0

    def draw(self, game):
        image = Player.images[self.facing][self.walkCount if self.facing != 0 else 0]
        game.blit(image, (self.x, self.y, Player.playerWidth, Player.playerHeight))

    #move first then update
    def move(self, direction):
        if self.stop >= Player.faceForward and direction == 0:
            self.facing = 0
            self.walkCount = 0
            self.stop = 0
        if direction == 1:
            self.facing = direction
            posx = self.x - self.speed
            self.x = max(-Player.playerWidth // 2, posx)
            self.walkCount = (self.walkCount + 1) % Player.numFrames
            self.stop = 0
        elif direction == 2:
            posx = self.x + self.speed
            self.facing = direction
            self.x = min(MAX_X - Player.playerWidth // 2, posx)
            self.walkCount = (self.walkCount + 1) % Player.numFrames
            self.stop = 0
        elif direction == 3:
            posy = self.y - self.speed
            self.y = max(MAX_Y - Player.yboundary, posy)
            self.walkCount = (self.walkCount + 1) % Player.numFrames
            self.stop = 0
        elif direction == 4:
            self.y = min(MAX_Y - Player.playerHeight, self.y + self.speed)
            self.walkCount = (self.walkCount + 1) % Player.numFrames
            self.stop = 0
        elif direction == 0 and self.facing != 0:
            self.stop += 1
        else:
            pass

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.jumpCount = Player.jumpFrames
        else:
            if self.jumpCount >= -Player.jumpFrames:
                neg = 1
                if self.jumpCount < 0:  # Coming down
                    neg = -1
                self.y -= (self.jumpCount ** 2) * 0.5 * neg
                self.jumpCount -= 1
            else:
                self.jumping = False
                self.jumpCount = Player.jumpFrames


