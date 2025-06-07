import pygame

class Obstacle:
    def __init__(self, x, y, width=26, height=26, color=(100, 0, 0), destructible=False, hp=1, blocks_movement=True, blocks_bullets=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.destructible = destructible
        self.hp = hp
        self.blocks_movement = blocks_movement
        self.blocks_bullets = blocks_bullets

        self.image = None
        if self.destructible:
            self.image = pygame.image.load("assets/brick.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (width, height))

    def hit(self, bullet=None):  # ← додати аргумент, але він необов’язковий
        if self.destructible:
            self.hp -= 1
            if self.hp <= 0:
                return True
        return False

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.color, self.rect)





class SteelBlock(Obstacle):
    def __init__(self, x, y):
        super().__init__(x, y, width=26, height=26, color=(150, 150, 150), destructible=False)
        self.image = pygame.image.load("assets/steel.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)



class WaterBlock(Obstacle):
    def __init__(self, x, y):
        super().__init__(x, y, color=(0, 0, 255), destructible=False, blocks_movement=True, blocks_bullets=False)

        self.images = [
            pygame.image.load("assets/water1.png").convert_alpha(),
            pygame.image.load("assets/water2.png").convert_alpha()
        ]
        self.images = [pygame.transform.scale(img, (self.rect.width, self.rect.height)) for img in self.images]

        self.image_index = 0
        self.animation_timer = 0
        self.animation_delay = 400  # мс між кадрами

    def draw(self, surface):
        now = pygame.time.get_ticks()
        if now - self.animation_timer > self.animation_delay:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.animation_timer = now

        surface.blit(self.images[self.image_index], self.rect.topleft)



class BushBlock(Obstacle):
    def __init__(self, x, y):
        super().__init__(x, y, color=(34, 139, 34), destructible=False, blocks_movement=False, blocks_bullets=False)
        self.image = pygame.image.load("assets/bush.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)