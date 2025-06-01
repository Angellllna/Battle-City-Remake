import pygame
from config import OBSTACLE_SIZE, COLOR_GRAY, PLAYER_SPEED, WINDOW_WIDTH, WINDOW_HEIGHT

class Enemy:
    def __init__(self, x, y, direction="horizontal"):
        self.rect = pygame.Rect(x, y, OBSTACLE_SIZE, OBSTACLE_SIZE)
        self.color = COLOR_GRAY
        self.speed = PLAYER_SPEED - 1
        self.direction = direction

    def move(self, obstacles):
        dx = dy = 0
        if self.direction == "horizontal":
            dx = self.speed
        elif self.direction == "vertical":
            dy = self.speed

        new_rect = self.rect.move(dx, dy)

        hit_wall = (
            new_rect.left < 0 or new_rect.right > WINDOW_WIDTH or
            new_rect.top < 0 or new_rect.bottom > WINDOW_HEIGHT
        )
        hit_obstacle = any(new_rect.colliderect(o.rect) for o in obstacles)

        if hit_wall or hit_obstacle:
            self.speed *= -1
        else:
            self.rect = new_rect

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
