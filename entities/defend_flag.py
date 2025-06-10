#Battle-City-Remake\entities\defend_flag.py
import pygame

class DefendFlag:
    def __init__(self, x, y):
        self.images = [
            pygame.image.load("assets/flagp_GRIN1.png").convert_alpha(),
            pygame.image.load("assets/flagp_GRIN2.png").convert_alpha()
        ]
        self.images = [pygame.transform.scale(img, (32, 78)) for img in self.images]

        self.image_index = 0
        self.animation_timer = 0
        self.animation_delay = 400  # мс між кадрами

        self.rect = self.images[0].get_rect(topleft=(x, y - 52))  # зміщення вгору

        self.capture_time = 7000  # 7 секунд на захоплення
        self.capturing = False
        self.capture_start = None
        self.captured = False

    def check_capture(self, enemy_tanks):
        if self.captured:
            return

        any_touching = False
        for enemy in enemy_tanks:
            if self.rect.colliderect(enemy.rect):
                any_touching = True
                break

        if any_touching:
            if not self.capturing:
                self.capturing = True
                self.capture_start = pygame.time.get_ticks()
        else:
            self.capturing = False
            self.capture_start = None

        if self.capturing:
            elapsed = pygame.time.get_ticks() - self.capture_start
            if elapsed >= self.capture_time:
                self.captured = True

    def draw(self, surface):
        # Анімація прапора
        now = pygame.time.get_ticks()
        if now - self.animation_timer > self.animation_delay:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.animation_timer = now

        image = self.images[self.image_index]
        surface.blit(image, self.rect.topleft)

        # Прогрес-бар
        if self.capturing and not self.captured:
            elapsed = pygame.time.get_ticks() - self.capture_start
            progress = min(elapsed / self.capture_time, 1.0)
            bar_width = int(self.rect.width * progress)
            pygame.draw.rect(surface, (255, 0, 0), (self.rect.left, self.rect.bottom + 4, bar_width, 4))
