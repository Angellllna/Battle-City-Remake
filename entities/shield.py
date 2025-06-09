import pygame
from config import OBSTACLE_SIZE, COLOR_BLUE

class Shield:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, OBSTACLE_SIZE, OBSTACLE_SIZE)

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_BLUE, self.rect)
