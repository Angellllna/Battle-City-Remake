import pygame

SHIELD_COLOR = (0, 100, 255)
SHIELD_SIZE = 50

class Shield:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, SHIELD_SIZE, SHIELD_SIZE)

    def draw(self, surface):
        pygame.draw.rect(surface, SHIELD_COLOR, self.rect)
