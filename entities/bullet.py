# DEFAULT FILE ⚠️

import pygame
from config import COLOR_WHITE

class Bullet:
    def __init__(self, x, y, dx, dy, speed=7):
        self.rect = pygame.Rect(x, y, 6, 6)
        self.dx = dx
        self.dy = dy
        self.speed = speed

    def move(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_WHITE, self.rect)
