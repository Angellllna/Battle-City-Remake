import random
import pygame
class Particle:
    def __init__(self, mx, my, image, speed_x=random.uniform(-2, 2), speed_y=random.uniform(-2, 2), size=random.randint(4, 16), color=(random.randint(90, 170), random.randint(0, 40), random.randint(190, 255))):
        self.rect = pygame.Rect(mx, my, size, size)
        self.image = pygame.image.load(f"Battle-City-Remake/textures/{image}.png").convert_alpha()
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
    def move(self):
        self.rect.x += self.speed_x + random.uniform(-0.1, 0.1)
        self.rect.y += self.speed_y + random.uniform(-0.1, 0.1)
        self.rect.h -= 0.6
        self.rect.w -= 0.6
    def draw(self, surface):
        scaled_image = pygame.transform.scale(self.image, (self.rect.h, self.rect.w))
        scaled_image.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
        img_rect = scaled_image.get_rect(center=self.rect.center)
        surface.blit(scaled_image, img_rect.topleft)