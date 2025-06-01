import pygame
from config import *
from utils.logger import any_error_logger, log

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.direction = (0, -1)  # directed to the upper side as default

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
                log(f"{PLAYER_NAME} moved to ({self.rect.x}, {self.rect.y})")
            else:
                log("{PLAYER_NAME} hit an obstacle!")
