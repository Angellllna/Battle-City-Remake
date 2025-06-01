import pygame
from config import *

class Obstacle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, OBSTACLE_SIZE, OBSTACLE_SIZE)

    def draw(self, surface):
        pygame.draw.rect(surface, OBSTACLE_COLOR, self.rect) 