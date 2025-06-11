import math
import os

import pygame

from config import PLAYER_HEALTH, PLAYER_SIZE, PLAYER_SPEED
from entities.bullet import Bullet


class Player:
    def __init__(self, position):
        self.collision_rect = pygame.Rect(
            position[0], position[1], PLAYER_SIZE, PLAYER_SIZE
        )
        self.speed = PLAYER_SPEED
        self.health = PLAYER_HEALTH
        self.bullets = []
        self.direction = pygame.Vector2(0, -1)

        try:
            self.images = [
                pygame.image.load(
                    os.path.join("textures", "tank111.png")
                ).convert_alpha(),
                pygame.image.load(
                    os.path.join("textures", "tank112.png")
                ).convert_alpha(),
            ]
            self.images = [
                pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE))
                for img in self.images
            ]
        except pygame.error as e:
            print(f"Error loading tank images: {e}")
            self.images = [pygame.Surface((PLAYER_SIZE, PLAYER_SIZE)) for _ in range(2)]
            for img in self.images:
                img.fill((0, 255, 0))

        self.image_index = 0
        self.image = self.images[self.image_index]

        self.animation_timer = 0
        self.animation_delay = 200  # мс
        self.moving = False

        self.current_angle = 0
        self.target_angle = 0
        self.rotation_speed = 10

        # Віддача
        self.recoil_offset = pygame.Vector2(0, 0)
        self.recoil_amount = 5
        self.recoil_return_speed = 1

        # Спалах пострілу
        self.muzzle_flash_image = pygame.image.load(
            os.path.join("textures", "muzzle_flash.png")
        ).convert_alpha()
        self.show_muzzle_flash = False
        self.muzzle_flash_timer = 0
        self.muzzle_flash_duration = 100  # мс

        # Звук пострілу
        self.shoot_sound = pygame.mixer.Sound(os.path.join("sounds", "shoot.mp3"))
        self.shoot_channel = pygame.mixer.Channel(2)

        # Звук мотора
        self.engine_sound = pygame.mixer.Sound(os.path.join("sounds", "engine.mp3"))
        self.engine_channel = pygame.mixer.Channel(1)

    def move(self, dx, dy, obstacles, keys):
        self.moving = dx != 0 or dy != 0
        if self.moving:
            new_direction = pygame.Vector2(dx, dy)
            if new_direction.length_squared() > 0:
                self.direction = new_direction.normalize()
                self.target_angle = self.get_angle_from_direction(self.direction)
            new_rect = self.collision_rect.move(dx * self.speed, dy * self.speed)
            for obstacle in obstacles:
                if obstacle.blocks_movement:
                    if new_rect.colliderect(obstacle.rect):
                        # Спробуємо ковзати вздовж перешкоди
                        new_rect_x = self.collision_rect.move(dx * self.speed, 0)
                        new_rect_y = self.collision_rect.move(0, dy * self.speed)
                        can_move_x = True
                        can_move_y = True
                        for obs in obstacles:
                            if obs.blocks_movement:
                                if new_rect_x.colliderect(obs.rect):
                                    can_move_x = False
                                if new_rect_y.colliderect(obs.rect):
                                    can_move_y = False
                        if can_move_x:
                            self.collision_rect = new_rect_x
                        elif can_move_y:
                            self.collision_rect = new_rect_y
                        return
            self.collision_rect = new_rect
        self.update()

    def get_angle_from_direction(self, direction):
        angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90
        return angle % 360

    def update(self):
        now = pygame.time.get_ticks()

        # Анімація
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

        self.image = pygame.transform.rotate(self.image, self.current_angle)

        # Віддача
        if self.recoil_offset.length_squared() > 0:
            self.recoil_offset -= (
                self.recoil_offset.normalize() * self.recoil_return_speed
            )
            if self.recoil_offset.length() < self.recoil_return_speed:
                self.recoil_offset = pygame.Vector2(0, 0)

        # Спалах пострілу
        if (
            self.show_muzzle_flash
            and now - self.muzzle_flash_timer > self.muzzle_flash_duration
        ):
            self.show_muzzle_flash = False

        # Звук мотора
        if self.moving:
            if not self.engine_channel.get_busy():
                self.engine_channel.play(self.engine_sound, loops=-1)
        else:
            if self.engine_channel.get_busy():
                self.engine_channel.stop()

    def shoot(self):
        if self.direction.length_squared() == 0:
            return
        bullet = Bullet(
            self.collision_rect.centerx - 2,
            self.collision_rect.centery - 2,
            self.direction.normalize(),
        )
        # self.bullets.append(bullet)

        # Віддача
        self.recoil_offset = -self.direction.normalize() * self.recoil_amount

        # Спалах пострілу
        self.show_muzzle_flash = True
        self.muzzle_flash_timer = pygame.time.get_ticks()

        # Звук пострілу через канал
        self.shoot_channel.play(self.shoot_sound)

        return bullet

    def draw(self, surface):
        draw_pos = pygame.Vector2(self.collision_rect.center) + self.recoil_offset
        img_rect = self.image.get_rect(center=draw_pos)
        surface.blit(self.image, img_rect.topleft)

        if self.show_muzzle_flash:
            muzzle_offset = self.direction.normalize() * 20
            flash_pos = (
                pygame.Vector2(self.collision_rect.center)
                + self.recoil_offset
                + muzzle_offset
            )
            flash_rect = self.muzzle_flash_image.get_rect(center=flash_pos)
            surface.blit(self.muzzle_flash_image, flash_rect.topleft)

        for bullet in self.bullets:
            pygame.draw.rect(surface, (255, 255, 0), bullet.rect)
