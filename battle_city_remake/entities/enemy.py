import pygame
import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import OBSTACLE_SIZE, COLOR_GRAY, PLAYER_SPEED, WINDOW_WIDTH, WINDOW_HEIGHT
ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
ENEMY_IMAGES = {
    "up": [
        pygame.image.load(os.path.join(ASSETS_DIR, 'enemy_1up.png')),
        pygame.image.load(os.path.join(ASSETS_DIR, 'enemy_2up.png'))
    ],
    "down": [
        pygame.image.load(os.path.join(ASSETS_DIR, 'enemy_1down.png')),
        pygame.image.load(os.path.join(ASSETS_DIR, 'enemy_2down.png'))
    ],
    "left": [
        pygame.image.load(os.path.join(ASSETS_DIR, 'enemy_1left.png')),
        pygame.image.load(os.path.join(ASSETS_DIR, 'enemy_2left.png'))
    ],
    "right": [
        pygame.image.load(os.path.join(ASSETS_DIR, 'enemy_1right.png')),
        pygame.image.load(os.path.join(ASSETS_DIR, 'enemy_2right.png'))
    ],
}

BULLET_SPEED = 5
BULLET_SIZE = 8

class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, BULLET_SIZE, BULLET_SIZE)
        self.color = (255, 0, 0)
        self.speed = BULLET_SPEED
        self.direction = direction

class Enemy:
    def __init__(self, x, y, direction=None):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.speed = 1
        self.directions = ["left", "right", "up", "down"]
        self.direction = direction or random.choice(self.directions)

        # текущие спрайты — берем для начального направления
        self.images = ENEMY_IMAGES[self.direction]
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_interval = 10

        # Для стрельбы
        self.bullets = []
        self.shoot_cooldown = 90
        self.shoot_timer = 0

    def change_direction(self, new_direction):
        if new_direction in self.directions and new_direction != self.direction:
            self.direction = new_direction
            self.images = ENEMY_IMAGES[self.direction]
            self.current_frame = 0  # сброс анимации

    def move(self, obstacles):
        dx = dy = 0
        if self.direction == "left":
            dx = -self.speed
        elif self.direction == "right":
            dx = self.speed
        elif self.direction == "up":
            dy = -self.speed
        elif self.direction == "down":
            dy = self.speed

        new_rect = self.rect.move(dx, dy)

        hit_wall = (
            new_rect.left < 0 or new_rect.right > 800 or
            new_rect.top < 0 or new_rect.bottom > 600
        )
        hit_obstacle = any(new_rect.colliderect(o.rect) for o in obstacles)

        if hit_wall or hit_obstacle:
            # При столкновении меняем направление (и обновляем спрайты)
            new_dir = random.choice([d for d in self.directions if d != self.direction])
            self.change_direction(new_dir)
        else:
            self.rect = new_rect

    def update_animation(self):
        self.frame_timer += 1
        if self.frame_timer >= self.frame_interval:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.images)

    def shoot(self):
        if self.shoot_timer <= 0:
            x, y = self.rect.center
            if self.direction == "left":
                x -= self.rect.width // 2
            elif self.direction == "right":
                x += self.rect.width // 2
            elif self.direction == "up":
                y -= self.rect.height // 2
            elif self.direction == "down":
                y += self.rect.height // 2

            bullet = Bullet(x, y, self.direction)
            self.bullets.append(bullet)
            self.shoot_timer = self.shoot_cooldown

    def update_bullets(self, obstacles, width, height):
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.off_screen(width, height):
                self.bullets.remove(bullet)
            else:
                for obs in obstacles:
                    if bullet.rect.colliderect(obs.rect):
                        self.bullets.remove(bullet)
                        break

    def update(self, obstacles, width, height):
        self.move(obstacles)
        self.update_animation()
        self.shoot()

        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        self.update_bullets(obstacles, width, height)

    def draw(self, surface):
        img = self.images[self.current_frame]
        surface.blit(img, self.rect)
        for bullet in self.bullets:
            bullet.draw(surface)