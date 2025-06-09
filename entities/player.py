import pygame
import math
from entities.bullet import Bullet
from config import PLAYER_SIZE, PLAYER_SPEED, PLAYER_HEALTH

class Player:
    def __init__(self, position):
        self.rect = pygame.Rect(position[0], position[1], PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.health = PLAYER_HEALTH
        self.bullets = []
        self.direction = pygame.Vector2(0, -1)

        try:
            self.images = [
                pygame.image.load("Battle-City-Remake/textures/tank1.png").convert_alpha(),
                pygame.image.load("Battle-City-Remake/textures/tank2.png").convert_alpha()
            ]
        except pygame.error as e:
            print(f"Error loading tank images: {e}")
            self.images = [pygame.Surface((PLAYER_SIZE, PLAYER_SIZE)) for _ in range(2)]
            for img in self.images:
                img.fill((0, 255, 0))
        self.image_index = 0
        self.image = self.images[self.image_index]

        self.animation_timer = 0
        self.animation_delay = 200  # ms
        self.moving = False
        self.current_angle = 0
        self.target_angle = 0
        self.rotation_speed = 10

    def move(self, dx, dy, obstacles, keys):
        self.moving = dx != 0 or dy != 0
        if self.moving:
            new_direction = pygame.Vector2(dx, dy)
            if new_direction.length_squared() > 0:
                self.direction = new_direction.normalize()
                self.target_angle = self.get_angle_from_direction(self.direction)
            new_rect = self.rect.move(dx * self.speed, dy * self.speed)
            for obstacle in obstacles:
                if obstacle.blocks_movement:
                    if new_rect.colliderect(obstacle.rect):
                        return  # Зіткнення з перешкодами
            self.rect = new_rect
        self.update()

    def get_angle_from_direction(self, direction):
        angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90
        return angle % 360
    
    def update(self):
        now = pygame.time.get_ticks()
        if self.moving and now - self.animation_timer > self.animation_delay:
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

        self.image = pygame.transform.rotate(self.images[self.image_index], self.current_angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self):
        if self.direction.length_squared() == 0:
            return None
        offset = 20  # Відстань від центру гравця
        bullet_x = self.rect.centerx + self.direction.x * offset - 2
        bullet_y = self.rect.centery + self.direction.y * offset - 2
        return Bullet(bullet_x, bullet_y, self.direction.normalize())

    def draw(self, surface):
        img_rect = self.image.get_rect(center=self.rect.center)
        surface.blit(self.image, img_rect.topleft)
        for bullet in self.bullets:
            bullet.draw(surface)