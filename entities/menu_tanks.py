import math
import random
import os
import pygame

from config import COLOR_BLACK, COLOR_WHITE, WINDOW_HEIGHT, WINDOW_WIDTH
from scenes.menu_scene import *
from utils.logger import log


import pygame
from config import COLOR_BLACK, COLOR_WHITE, WINDOW_HEIGHT, WINDOW_WIDTH
from scenes.menu_scene import *
from utils.logger import log


class Bullet:
    def __init__(self, x, y, dx, dy, color):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.speed = 5
        self.width = 4
        self.height = 4
        self.rect = pygame.Rect(
            self.x - self.width // 2, self.y - self.height // 2, self.width, self.height
        )

    def move(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        self.rect.x = self.x - self.width // 2
        self.rect.y = self.y - self.height // 2

    def draw(self, screen):
        pygame.draw.circle(
            screen, self.color, (int(self.x), int(self.y)), self.width // 2
        )


class Tank:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.width = 40
        self.height = 40
        self.speed = 2
        self.direction = random.choice(["up", "down", "left", "right"])
        self.last_shot_time = pygame.time.get_ticks()
        self.shots = []
        try:
            self.images = [
                pygame.image.load(
                    os.path.join("textures", "tank331.png")
                ).convert_alpha(),
                pygame.image.load(
                    os.path.join("textures", "tank332.png")
                ).convert_alpha(),
            ]
            self.images = [
                pygame.transform.scale(img, (self.width, self.height))
                for img in self.images
            ]
            for img in self.images:
                img.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
        except pygame.error as e:
            log(f"🔴 Не вдалося завантажити зображення танка: {e}")
            self.images = [pygame.Surface((self.width, self.height)) for _ in range(2)]
            for img in self.images:
                img.fill(self.color)
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.animation_timer = 0
        self.animation_delay = 200
        self.current_angle = self.get_angle_from_direction()
        self.target_angle = self.current_angle
        self.rotation_speed = 10
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.health = 3  # Додаємо здоров’я для танків

    def get_angle_from_direction(self):
        if self.direction == "up":
            return 0
        elif self.direction == "right":
            return 270
        elif self.direction == "down":
            return 180
        elif self.direction == "left":
            return 90
        return 0

    def move(self, obstacles):
        dx = dy = 0
        if self.direction == "up":
            dy = -self.speed
        elif self.direction == "down":
            dy = self.speed
        elif self.direction == "left":
            dx = -self.speed
        elif self.direction == "right":
            dx = self.speed

        if dx != 0 or dy != 0:
            new_rect = self.rect.move(dx, dy)
            collision = False
            for obstacle in obstacles:
                if obstacle.blocks_movement and new_rect.colliderect(obstacle.rect):
                    collision = True
                    break
            if not collision:
                self.rect = new_rect
                self.x = self.rect.x
                self.y = self.rect.y
            else:
                self.direction = random.choice(["up", "down", "left", "right"])
                self.target_angle = self.get_angle_from_direction()

        self.x = max(0, min(self.x, WINDOW_WIDTH - self.width))
        self.y = max(0, min(self.y, WINDOW_HEIGHT - self.height))
        self.rect.x = self.x
        self.rect.y = self.y

        if random.random() < 0.02:
            self.direction = random.choice(["up", "down", "left", "right"])
            self.target_angle = self.get_angle_from_direction()

        self.update_animation()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > 1000:
            dx, dy = 0, 0
            if self.direction == "up":
                dy = -1
            elif self.direction == "down":
                dy = 1
            elif self.direction == "left":
                dx = -1
            elif self.direction == "right":
                dx = 1
            bullet = Bullet(
                self.x + self.width // 2, self.y + self.height // 2, dx, dy, self.color
            )
            self.shots.append(bullet)
            self.last_shot_time = now

    def shoot_at(self, target):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > 1000:
            dx = target.x + target.width // 2 - (self.x + self.width // 2)
            dy = target.y + target.height // 2 - (self.y + self.height // 2)
            distance = math.hypot(dx, dy)
            if distance == 0:
                distance = 1
            dx /= distance
            dy /= distance
            bullet = Bullet(
                self.x + self.width // 2, self.y + self.height // 2, dx, dy, self.color
            )
            self.shots.append(bullet)
            self.last_shot_time = now

    def hit(self):
        self.health -= 1
        log(f"💥 Танк ({self.color}) отримав урон! Здоров’я: {self.health}")
        return self.health <= 0  # Повертаємо True, якщо танк знищено

    def update(self, target, obstacles):
        self.move(obstacles)
        self.shoot_at(target)
        bullets_to_remove = []
        obstacles_to_destroy = []
        for bullet in self.shots[:]:
            bullet.move()
            # Перевірка меж екрана
            if not (0 <= bullet.x <= WINDOW_WIDTH and 0 <= bullet.y <= WINDOW_HEIGHT):
                bullets_to_remove.append(bullet)
                continue
            # Перевірка зіткнення з перешкодами
            for obstacle in obstacles:
                if bullet.rect.colliderect(obstacle.rect):
                    if obstacle.blocks_bullets:  # Перевірка blocks_bullet
                        if hasattr(obstacle, "hit") and obstacle.destructible:
                            obstacle.hit(bullet)
                            if obstacle.hp <= 0:
                                obstacles_to_destroy.append(obstacle)
                        bullets_to_remove.append(bullet)
                        log("🧱 Bullet hit obstacle")
                        break
            # Перевірка зіткнення з цільним танком
            else:
                if bullet.rect.colliderect(target.rect) and target != self:
                    if target.hit():
                        log("💥 Tank destroyed!")
                    bullets_to_remove.append(bullet)
                    log("✅ Bullet hit target tank")
                    break

        # Видалення куль
        for bullet in bullets_to_remove:
            if bullet in self.shots:
                self.shots.remove(bullet)

        return bullets_to_remove, obstacles_to_destroy

    def update_animation(self):
        now = pygame.time.get_ticks()
        if now - self.animation_timer > self.animation_delay:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.animation_timer = now
        diff = (self.target_angle - self.current_angle) % 360
        if diff > 180:
            diff -= 360
        if abs(diff) < self.rotation_speed:
            self.current_angle = self.target_angle
        else:
            self.current_angle += self.rotation_speed * (1 if diff > 0 else -1)
            self.current_angle %= 360
        self.image = pygame.transform.rotate(
            self.images[self.image_index], self.current_angle
        )

    def draw(self, screen):
        img_rect = self.image.get_rect(
            center=(self.x + self.width // 2, self.y + self.height // 2)
        )
        screen.blit(self.image, img_rect.topleft)
        for bullet in self.shots:
            bullet.draw(screen)
