import random
import pygame

class Particle:
    def __init__(self, mx, my, image, speed_x=random.uniform(-2, 2), speed_y=random.uniform(-2, 2), size=random.randint(4, 16), color=(random.randint(90, 170), random.randint(0, 40), random.randint(190, 255))):
        self.x = float(mx)
        self.y = float(my)
        self.width = float(size)
        self.height = float(size)
        self.rect = pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))
        try:
            self.image = pygame.image.load(f"textures/{image}.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (int(self.width), int(self.height)))
        except pygame.error as e:
            print(f"Error loading particle image: {e}")
            self.image = pygame.Surface((int(self.width), int(self.height)))
            self.image.fill(color)
        self.color = color
        self.speed_x = float(speed_x)
        self.speed_y = float(speed_y)

    def move(self):
        self.x += self.speed_x + random.uniform(-0.1, 0.1)
        self.y += self.speed_y + random.uniform(-0.1, 0.1)
        self.width -= 0.3
        self.height -= 0.3
        self.rect = pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))

    def draw(self, surface):
        scaled_image = pygame.transform.scale(self.image, (int(self.width), int(self.height)))
        tinted_image = scaled_image.copy()
        tinted_image.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
        img_rect = tinted_image.get_rect(center=(int(self.x + self.width / 2), int(self.y + self.height / 2)))
        surface.blit(tinted_image, img_rect.topleft)