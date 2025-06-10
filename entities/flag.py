# Battle-City-Remake\entities\flag.pyimport pygame
import pygame
class Flag:
    def __init__(self, x, y):
        # Червоні (за замовчуванням)
        self.red_images = [
            pygame.image.load("assets/flagp_RID1.png").convert_alpha(),
            pygame.image.load("assets/flagp_RID2.png").convert_alpha()
        ]
        # Сірі
        self.gray_images = [
            pygame.image.load("assets/flagp_CEP1.png").convert_alpha(),
            pygame.image.load("assets/flagp_CEP2.png").convert_alpha()
        ]
        # Зелені
        self.green_images = [
            pygame.image.load("assets/flagp_GRIN1.png").convert_alpha(),
            pygame.image.load("assets/flagp_GRIN2.png").convert_alpha()
        ]

        # Масштабуємо всі
        for i in range(2):
            self.red_images[i] = pygame.transform.scale(self.red_images[i], (32, 78))
            self.gray_images[i] = pygame.transform.scale(self.gray_images[i], (32, 78))
            self.green_images[i] = pygame.transform.scale(self.green_images[i], (32, 78))

        self.image_index = 0
        self.animation_timer = 0
        self.animation_delay = 400  # мс

        self.rect = self.red_images[0].get_rect(topleft=(x, y - 52))

        self.capture_time = 7000  # 7 секунд
        self.capturing = False
        self.capture_start = None
        self.captured = False

        self.blink_toggle = False  # для перемикання між сірим і зеленим

    def check_capture(self, player):
        if self.captured:
            return

        if self.rect.colliderect(player.rect):
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
        now = pygame.time.get_ticks()

        if now - self.animation_timer > self.animation_delay:
            self.image_index = (self.image_index + 1) % 2
            self.blink_toggle = not self.blink_toggle
            self.animation_timer = now

        # Вибираємо набір кадрів
        if self.captured:
            images = self.green_images
        elif self.capturing:
            images = self.green_images if self.blink_toggle else self.gray_images
        else:
            images = self.red_images

        image = images[self.image_index]
        surface.blit(image, self.rect.topleft)

        # Прогрес-бар захоплення
        if self.capturing and not self.captured:
            elapsed = pygame.time.get_ticks() - self.capture_start
            progress = min(elapsed / self.capture_time, 1.0)
            bar_width = int(self.rect.width * progress)
            pygame.draw.rect(surface, (0, 255, 0), (self.rect.left, self.rect.bottom + 4, bar_width, 4))
