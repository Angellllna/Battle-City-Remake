import pygame
import math
from entities.bullet import Bullet

class Player:
    def __init__(self, position, speed=2):
        self.rect = pygame.Rect(position[0], position[1], 26, 26)
        self.speed = speed
        self.bullets = []
        self.direction = pygame.Vector2(0, -1)

        self.images = [
            pygame.image.load("assets/tank1.png").convert_alpha(),
            pygame.image.load("assets/tank2.png").convert_alpha()
        ]
        self.image_index = 0
        self.image = self.images[self.image_index]

        self.animation_timer = 0
        self.animation_delay = 200  # мс
        self.moving = False

        self.current_angle = 0
        self.target_angle = 0
        self.rotation_speed = 10

    def move(self, dx, dy, obstacles):
        self.moving = dx != 0 or dy != 0
        if self.moving:
            new_direction = pygame.Vector2(dx, dy)
            if new_direction != self.direction:
                self.direction = new_direction
                self.target_angle = self.get_angle_from_direction(self.direction)

            new_rect = self.rect.move(dx * self.speed, dy * self.speed)
            for obstacle in obstacles:
                if obstacle.blocks_movement:
                    if hasattr(obstacle, "get_collision_rects"):
                        for seg_rect in obstacle.get_collision_rects():
                            if new_rect.colliderect(seg_rect):
                                return
                    elif new_rect.colliderect(obstacle.rect):
                        return
            self.rect = new_rect

    def get_angle_from_direction(self, direction):
        angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90
        return angle % 360

    def update(self):
        now = pygame.time.get_ticks()

        # Обробка анімації руху
        if self.moving and now - self.animation_timer > self.animation_delay:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.animation_timer = now
        self.image = self.images[self.image_index]

        # Поворот
        diff = (self.target_angle - self.current_angle) % 360
        if diff > 180:
            diff -= 360
        if abs(diff) < self.rotation_speed:
            self.current_angle = self.target_angle
        else:
            self.current_angle += self.rotation_speed * (1 if diff > 0 else -1)
            self.current_angle %= 360

        # Повертаємо танк
        self.image = pygame.transform.rotate(self.image, self.current_angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self):
        if self.direction.length_squared() == 0:
            return
        bullet = Bullet(self.rect.centerx - 2, self.rect.centery - 2, self.direction.normalize())
        self.bullets.append(bullet)

    def update_bullets(self, screen_rect):
        for bullet in self.bullets[:]:
            bullet.move()
            if not screen_rect.contains(bullet.rect):
                self.bullets.remove(bullet)

    def draw(self, surface):
        img_rect = self.image.get_rect(center=self.rect.center)
        surface.blit(self.image, img_rect.topleft)
        for bullet in self.bullets:
            pygame.draw.rect(surface, (255, 255, 0), bullet.rect)
