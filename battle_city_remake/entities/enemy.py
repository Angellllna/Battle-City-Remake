import pygame
import random
import config
from config import *


class Enemy:
    def __init__(self, x, y, direction="horizontal"):
        self.rect = pygame.Rect(x, y, OBSTACLE_SIZE, OBSTACLE_SIZE)
        self.color = GRAY
        self.speed = PLAYER_SPEED - 1  # повільніше за гравця
        self.direction = direction  # 'horizontal' or 'vertical'

    def move(self, obstacles):
        dx = dy = 0

        if self.direction == "horizontal":
            dx = self.speed
        elif self.direction == "vertical":
            dy = self.speed

        new_rect = self.rect.move(dx, dy)

        # Перевірка на зіткнення з перешкодою або вихід за межі екрана
        hit_wall = (
            new_rect.left < 0 or new_rect.right > WIN_WIDTH or
            new_rect.top < 0 or new_rect.bottom > WIN_HEIGHT
        )
        hit_obstacle = any(new_rect.colliderect(o.rect) for o in obstacles)

        if hit_wall or hit_obstacle:
            self.speed *= -1  # Розвертаємось
        else:
            self.rect = new_rect

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
