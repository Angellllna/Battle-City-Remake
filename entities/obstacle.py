import pygame

class Obstacle:
    def __init__(self, x, y, width=32, height=32, color=(100, 0, 0), destructible=False, hp=1, blocks_movement=True, blocks_bullets=True):
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
        super().__init__(x, y, width=32, height=32, color=(150, 150, 150), destructible=False)

        # Зображення сталі
        self.image = pygame.image.load("assets/steel.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))

        # Іскра
        self.spark_image = pygame.image.load("assets/spark.png").convert_alpha()
        self.spark_image = pygame.transform.scale(self.spark_image, (self.rect.width, self.rect.height))

        self.spark_visible = False
        self.spark_timer = 0
        self.spark_duration = 100  # мс
        self.spark_offset = (0, 0)

        # 🎵 Звук удару
        self.hit_sound = pygame.mixer.Sound("assets/hit-metal.mp3")

    def hit(self, bullet=None):
        if bullet:
            bx, by = bullet.rect.center
            sx, sy = self.rect.center

            offset_x = bx - sx
            offset_y = by - sy

            if abs(offset_x) > abs(offset_y):
                self.spark_offset = (-self.rect.width // 2, 0) if offset_x < 0 else (self.rect.width // 2, 0)
            else:
                self.spark_offset = (0, -self.rect.height // 2) if offset_y < 0 else (0, self.rect.height // 2)
        else:
            self.spark_offset = (0, 0)

        self.spark_visible = True
        self.spark_timer = pygame.time.get_ticks()

        # ▶️ Програти звук
        self.hit_sound.play()

        return False

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

        if self.spark_visible:
            now = pygame.time.get_ticks()
            if now - self.spark_timer < self.spark_duration:
                spark_pos = (
                    self.rect.centerx + self.spark_offset[0] - self.rect.width // 2,
                    self.rect.centery + self.spark_offset[1] - self.rect.height // 2
                )
                surface.blit(self.spark_image, spark_pos)
            else:
                self.spark_visible = False






class WaterBlock(Obstacle):
    def __init__(self, x, y):
        super().__init__(x, y, width=32, height=32, color=(0, 0, 255), destructible=False, blocks_movement=True, blocks_bullets=False)

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
        super().__init__(x, y, width=32, height=32, color=(34, 139, 34), destructible=False, blocks_movement=False, blocks_bullets=False)
        self.image = pygame.image.load("assets/bush.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
