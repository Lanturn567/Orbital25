import pygame

MAX_X, MAX_Y = 740, 493

class OpeningPlayer:
    images = []
    numFrames = 4
    playerWidth = 32
    playerHeight = 64
    playerSpeed = 10
    jumpFrames = 8
    faceForward = 14
    yboundary = 100

    @classmethod
    def init_images(cls):

        for dir in ["Front", "Left", "Right", "Back"]:
            sheet = pygame.image.load("./Player/walk" + dir + ".png").convert_alpha()
            frame_width = sheet.get_width() // cls.numFrames
            frame_height = sheet.get_height()
            curr = []
            for i in range(cls.numFrames):
                frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)).copy()
                curr.append(frame)
            cls.images.append(curr)


    def __init__(self):
        self.x = MAX_X // 2
        self.y = MAX_Y - OpeningPlayer.playerHeight - 10
        self.walkCount = 0
        self.jumpCount = OpeningPlayer.jumpFrames
        self.facing = 0 # 1 left, 0 forward, 2 right
        self.jumping = False
        self.speed = OpeningPlayer.playerSpeed
        self.stop = 0

    def draw(self, game):
        image = OpeningPlayer.images[self.facing][self.walkCount if self.facing != 0 else 0]
        game.blit(image, (self.x, self.y, OpeningPlayer.playerWidth, OpeningPlayer.playerHeight))

    #move first then update
    def move(self, direction):
        if self.stop >= OpeningPlayer.faceForward and direction == 0:
            self.facing = 0
            self.walkCount = 0
            self.stop = 0
        if direction == 1:
            self.facing = direction
            posx = self.x - self.speed
            self.x = max(-OpeningPlayer.playerWidth // 2, posx)
            self.walkCount = (self.walkCount + 1) % OpeningPlayer.numFrames
            self.stop = 0
        elif direction == 2:
            posx = self.x + self.speed
            self.facing = direction
            self.x = min(MAX_X - OpeningPlayer.playerWidth // 2, posx)
            self.walkCount = (self.walkCount + 1) % OpeningPlayer.numFrames
            self.stop = 0
        elif direction == 3:
            posy = self.y - self.speed
            self.y = max(MAX_Y - OpeningPlayer.yboundary, posy)
            self.walkCount = (self.walkCount + 1) % OpeningPlayer.numFrames
            self.stop = 0
        elif direction == 4:
            self.y = min(MAX_Y - OpeningPlayer.playerHeight, self.y + self.speed)
            self.walkCount = (self.walkCount + 1) % OpeningPlayer.numFrames
            self.stop = 0
        elif direction == 0 and self.facing != 0:
            self.stop += 1
        else:
            pass

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.jumpCount = OpeningPlayer.jumpFrames
        else:
            if self.jumpCount >= -OpeningPlayer.jumpFrames:
                neg = 1
                if self.jumpCount < 0:  # Coming down
                    neg = -1
                self.y -= (self.jumpCount ** 2) * 0.5 * neg
                self.jumpCount -= 1
            else:
                self.jumping = False
                self.jumpCount = OpeningPlayer.jumpFrames


