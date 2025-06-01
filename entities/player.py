import pygame
from config import COLOR_RED, PLAYER_SPEED, PLAYER_SIZE, PLAYER_HEALTH
from utils.logger import log
from entities.bullet import Bullet

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.health = PLAYER_HEALTH
        self.direction = (0, -1)

    def move(self, keys, obstacles):
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -PLAYER_SPEED
            self.direction = (-1, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = PLAYER_SPEED
            self.direction = (1, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -PLAYER_SPEED
            self.direction = (0, -1)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = PLAYER_SPEED
            self.direction = (0, 1)

        new_rect = self.rect.move(dx, dy)
        if dx != 0 or dy != 0:
            if not any(new_rect.colliderect(o.rect) for o in obstacles):
                self.rect = new_rect
                log(f"➡️ Player moved to ({self.rect.x}, {self.rect.y})")
            else:
                log("❌ Player hit an obstacle!")

    def shoot(self):
        bx = self.rect.centerx - 3
        by = self.rect.centery - 3
        dx, dy = self.direction
        return Bullet(bx, by, dx, dy)

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_RED, self.rect)
