import pygame
import math
from entities.obstacle import Shield

class Enemy:
    def __init__(self, position, speed=1):
        self.rect = pygame.Rect(position[0], position[1], 26, 26)
        self.speed = speed
        self.image = pygame.image.load("assets/enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (26, 26))

    def move_towards(self, target_pos):
        direction = pygame.Vector2(target_pos[0] - self.rect.centerx, target_pos[1] - self.rect.centery)
        if direction.length_squared() != 0:
            direction = direction.normalize()
            self.rect.x += int(direction.x * self.speed)
            self.rect.y += int(direction.y * self.speed)

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
