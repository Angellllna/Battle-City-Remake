import pygame
class Bullet:
    def __init__(self, x, y, direction, speed=5):
        self.rect = pygame.Rect(x, y, 4, 4)
        self.direction = direction
        self.speed = speed

    def move(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed