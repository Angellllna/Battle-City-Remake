import pygame
from config import COLOR_WHITE, COLOR_RED

class Bullet:
    def __init__(self, x, y, direction, speed=7):
        self.rect = pygame.Rect(x, y, 6, 6)
        self.direction = direction
        self.speed = speed
        try:
            self.image = pygame.image.load("Battle-City-Remake/textures/bullet.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (16, 8))
        except pygame.error as e:
            print(f"Error loading bullet image: {e}")
            self.image = None
            self.color = COLOR_WHITE

    def move(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

class Missile:
    def __init__(self, x, y, direction, speed=5):
        self.rect = pygame.Rect(x, y, 8, 8)
        self.direction = direction
        self.speed = speed
        try:
            self.image = pygame.image.load("Battle-City-Remake/textures/missile.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (8, 8))
        except pygame.error as e:
            print(f"Error loading missile image: {e}")
            self.image = None
            self.color = COLOR_RED

    def move(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.color, self.rect)