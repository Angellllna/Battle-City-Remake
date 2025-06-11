import os

import pygame

from config import COLOR_RED, COLOR_WHITE


class Bullet:
    def __init__(self, x, y, direction, speed=7):
        self.rect = pygame.Rect(x, y, 10, 10)
        self.direction = direction
        self.speed = speed
        try:
            self.image = pygame.image.load(
                os.path.join("textures", "bullet.png")
            ).convert_alpha()
            self.image = pygame.transform.scale(self.image, (10, 10))
            self.image.fill((255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
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
    def __init__(self, x, y, direction, speed=5, damage=1):
        self.rect = pygame.Rect(x, y, 10, 10)
        self.direction = direction
        self.speed = speed
        self.damage = damage
        try:
            self.image = pygame.image.load(
                os.path.join("textures", "bullet.png")
            ).convert_alpha()
            self.image = pygame.transform.scale(self.image, (10, 10))
            self.image.fill((255, 150, 150), special_flags=pygame.BLEND_RGBA_MULT)
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
