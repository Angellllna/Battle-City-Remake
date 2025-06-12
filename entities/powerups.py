import pygame
import random
from config import OBSTACLE_SIZE

class Part:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, OBSTACLE_SIZE // 2, OBSTACLE_SIZE // 2)
        self.type = random.choice(["speed", "speed", "health", "health", "damage", "damage", "fire_rate", "fire_rate", "repair", "repair", "repair", "repair", "shield", "turret"])
        self.color = {
            "speed": (0, 0, 255),      # Green for speed
            "health": (0, 255, 0),     # Red for health
            "damage": (255, 0, 0),   # Yellow for damage
            "fire_rate": (255, 255, 0),   # Blue for fire rate
            "repair": (0, 255, 0),
            "shield": (0, 255, 255),
            "turret": (255, 255, 0)
        }[self.type]
        try:
            if self.type == "repair":
                self.image = pygame.image.load(f"textures/repair.png").convert_alpha()
            elif self.type == "shield":
                self.image = pygame.image.load(f"textures/shield1.png").convert_alpha()
            elif self.type == "turret":
                self.image = pygame.image.load(f"textures/turret.png").convert_alpha()
            else:
                self.image = pygame.image.load(f"textures/powerup.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (OBSTACLE_SIZE // 2, OBSTACLE_SIZE // 2))
            self.image.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
        except pygame.error:
            self.image = pygame.Surface((OBSTACLE_SIZE // 2, OBSTACLE_SIZE // 2))
            self.image.fill(self.color)

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        