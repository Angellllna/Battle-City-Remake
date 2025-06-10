import random
import pygame

class Particle:
    def __init__(self, mx, my, image, speed_x=random.uniform(-2, 2), speed_y=random.uniform(-2, 2), size=random.randint(4, 16), color=(random.randint(90, 170), random.randint(0, 40), random.randint(190, 255))):
        self.rect = pygame.Rect(mx, my, size, size)
        try:
            self.image = pygame.image.load(f"Battle-City-Remake/textures/{image}.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (size, size))
        except pygame.error as e:
            print(f"Error loading particle image: {e}")
            self.image = pygame.Surface((size, size))
            self.image.fill(color)
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y

    def move(self):
        self.rect.x += self.speed_x + random.uniform(-0.1, 0.1)
        self.rect.y += self.speed_y + random.uniform(-0.1, 0.1)
        self.rect.h -= 0.6
        self.rect.w -= 0.6

    def draw(self, surface):
        scaled_image = pygame.transform.scale(self.image, (int(self.rect.w), int(self.rect.h)))
        # Apply color tint to the image
        tinted_image = scaled_image.copy()
        tinted_image.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
        img_rect = tinted_image.get_rect(center=self.rect.center)
        surface.blit(tinted_image, img_rect.topleft)