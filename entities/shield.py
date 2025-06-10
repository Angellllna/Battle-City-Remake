import pygame

SHIELD_TEXTURES = ["assets/shield-1.png", "assets/shield-2.png", "assets/shield-3.png", "assets/shield-4.png"]
SHIELD_SIZE = 32

class Shield:
    def __init__(self, x, y, move_direction, speed):
        self.rect = pygame.Rect(x, y, SHIELD_SIZE, SHIELD_SIZE)

        self.images = [ pygame.image.load(texture).convert_alpha() for texture in SHIELD_TEXTURES ]
        self.images = [pygame.transform.scale(img, (self.rect.width, self.rect.height)) for img in self.images]

        self.image_index = 0
        self.animation_timer = 0
        self.animation_delay = 300

    def draw(self, surface):
        now = pygame.time.get_ticks()
        if now - self.animation_timer > self.animation_delay:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.animation_timer = now

        surface.blit(self.images[self.image_index], self.rect.topleft)