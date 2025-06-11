import os
import random

import pygame

from config import COLOR_BLUE, OBSTACLE_SIZE
from entities.enemy import (
    BaseChasingShootingEnemy,
    ChasingEnemy,
    Enemy,
    FlagChasingEnemy,
    RandomShootingEnemy,
    ShootingEnemy,
)


class Obstacle:
    def __init__(
        self,
        x,
        y,
        width=OBSTACLE_SIZE,
        height=OBSTACLE_SIZE,
        color=(100, 0, 0),
        destructible=False,
        hp=1,
        blocks_movement=True,
        blocks_bullets=True,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.destructible = destructible
        self.hp = hp
        self.blocks_movement = blocks_movement
        self.blocks_bullets = blocks_bullets
        self.image = None
        if self.destructible:
            try:
                self.image = pygame.image.load("textures/brick.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (width, height))
            except pygame.error as e:
                print(f"Error loading brick image: {e}")

        self.segments = {"tl": True, "tr": True, "bl": True, "br": True}

        # Прямокутники сегментів
        self.offset_x = width // 2
        self.offset_y = height // 2
        self.segment_rects = {
            "tl": pygame.Rect(x, y, self.offset_x, self.offset_y),
            "tr": pygame.Rect(x + self.offset_x, y, self.offset_x, self.offset_y),
            "bl": pygame.Rect(x, y + self.offset_y, self.offset_x, self.offset_y),
            "br": pygame.Rect(
                x + self.offset_x, y + self.offset_y, self.offset_x, self.offset_y
            ),
        }

    def hit(self, bullet=None):
        if self.destructible:
            for key, seg_rect in self.segment_rects.items():
                if self.segments[key] and bullet.rect.colliderect(seg_rect):
                    self.segments[key] = False
                    break
            return not any(self.segments.values())
        return False

    def draw(self, surface):
        for key, alive in self.segments.items():
            if alive:
                seg_rect = self.segment_rects[key]
                if key == "tl":
                    area = pygame.Rect(0, 0, self.offset_x, self.offset_y)
                elif key == "tr":
                    area = pygame.Rect(self.offset_x, 0, self.offset_x, self.offset_y)
                elif key == "bl":
                    area = pygame.Rect(0, self.offset_y, self.offset_x, self.offset_y)
                elif key == "br":
                    area = pygame.Rect(
                        self.offset_x, self.offset_y, self.offset_x, self.offset_y
                    )
                surface.blit(self.image, seg_rect.topleft, area)

    def get_collision_rects(self):
        # Повертає лише живі сегменти
        return [r for k, r in self.segment_rects.items() if self.segments[k]]


class SteelBlock(Obstacle):
    def __init__(self, x, y):
        super().__init__(
            x,
            y,
            width=OBSTACLE_SIZE,
            height=OBSTACLE_SIZE,
            color=(100, 100, 100),
            destructible=False,
        )
        try:
            self.image = pygame.image.load("textures/steel.png").convert_alpha()
            self.image = pygame.transform.scale(
                self.image, (self.rect.width, self.rect.height)
            )
            self.image.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
        except pygame.error as e:
            print(f"Error loading steel image: {e}")

        # Іскра
        self.spark_image = pygame.image.load(
            os.path.join("textures", "spark.png")
        ).convert_alpha()
        self.spark_image = pygame.transform.scale(
            self.spark_image, (self.rect.width, self.rect.height)
        )

        self.spark_visible = False
        self.spark_timer = 0
        self.spark_duration = 100  # мс
        self.spark_offset = (0, 0)

        # 🎵 Звук удару
        self.hit_sound = pygame.mixer.Sound(os.path.join("sounds", "hit-metal.mp3"))

    def hit(self, bullet=None):
        if bullet:
            bx, by = bullet.rect.center
            sx, sy = self.rect.center

            offset_x = bx - sx
            offset_y = by - sy

            if abs(offset_x) > abs(offset_y):
                self.spark_offset = (
                    (-self.rect.width // 2, 0)
                    if offset_x < 0
                    else (self.rect.width // 2, 0)
                )
            else:
                self.spark_offset = (
                    (0, -self.rect.height // 2)
                    if offset_y < 0
                    else (0, self.rect.height // 2)
                )
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
                    self.rect.centery + self.spark_offset[1] - self.rect.height // 2,
                )
                surface.blit(self.spark_image, spark_pos)
            else:
                self.spark_visible = False


class WaterBlock(Obstacle):
    def __init__(self, x, y):
        super().__init__(
            x,
            y,
            color=(0, 255, 255),
            destructible=False,
            blocks_movement=True,
            blocks_bullets=False,
        )
        self.images = []
        try:
            self.images = [
                pygame.image.load("textures/water1.png").convert_alpha(),
                pygame.image.load("textures/water2.png").convert_alpha(),
            ]
            self.images = [
                pygame.transform.scale(img, (self.rect.width, self.rect.height))
                for img in self.images
            ]
        except pygame.error as e:
            print(f"Error loading water images: {e}")
        self.image_index = 0
        self.animation_timer = 0
        self.animation_delay = 400

    def draw(self, surface):
        now = pygame.time.get_ticks()
        if now - self.animation_timer > self.animation_delay:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.animation_timer = now
        if self.images:
            surface.blit(self.images[self.image_index], self.rect.topleft)


class BushBlock(Obstacle):
    def __init__(self, x, y):
        super().__init__(
            x,
            y,
            color=(34, 139, 34),
            destructible=False,
            blocks_movement=False,
            blocks_bullets=False,
        )
        try:
            self.image = pygame.image.load(
                os.path.join("textures", "bush.png")
            ).convert_alpha()
            self.image = pygame.transform.scale(
                self.image, (self.rect.width, self.rect.height)
            )
        except pygame.error as e:
            print(f"Error loading bush image: {e}")

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect.topleft)


class Shield(Obstacle):
    def __init__(self, x, y):
        super().__init__(
            x,
            y,
            width=OBSTACLE_SIZE,
            height=OBSTACLE_SIZE,
            color=COLOR_BLUE,
            destructible=False,
            blocks_movement=False,
            blocks_bullets=True,
        )

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


class DefendFlag:
    def __init__(self, x, y):
        self.images = []
        self.captured_images = []
        try:
            self.images = [
                pygame.image.load("textures/flag_GREEN1.png").convert_alpha(),
                pygame.image.load("textures/flag_GREEN2.png").convert_alpha(),
            ]
            self.captured_images = [
                pygame.image.load("textures/flag_RED1.png").convert_alpha(),
                pygame.image.load("textures/flag_RED2.png").convert_alpha(),
            ]
            self.images = [
                pygame.transform.scale(img, (OBSTACLE_SIZE, OBSTACLE_SIZE))
                for img in self.images
            ]
            self.captured_images = [
                pygame.transform.scale(img, (OBSTACLE_SIZE, OBSTACLE_SIZE))
                for img in self.captured_images
            ]
        except pygame.error as e:
            print(f"Error loading flag images: {e}")
            self.images = [
                pygame.Surface((OBSTACLE_SIZE, OBSTACLE_SIZE)) for _ in range(2)
            ]
            self.captured_images = [
                pygame.Surface((OBSTACLE_SIZE, OBSTACLE_SIZE)) for _ in range(2)
            ]
            for img in self.images:
                img.fill((255, 255, 255))
            for img in self.captured_images:
                img.fill((255, 0, 0))
        self.image_index = 0
        self.animation_timer = 0
        self.animation_delay = 400
        self.rect = self.images[0].get_rect(topleft=(x, y))
        self.captured = False
        self.recapture_time = 0
        self.recapturing = False
        self.recapture_duration = 5000  # 5 seconds in milliseconds
        self.font = pygame.font.SysFont("arial", 16)

    def check_capture(self, enemy_tanks):
        if self.captured:
            return
        for enemy in enemy_tanks:
            if self.rect.colliderect(enemy.collision_rect):
                self.captured = True
                print(f"Flag captured by enemy at ({self.rect.x}, {self.rect.y})")
                break

    def check_recapture(self, player):
        if not self.captured:
            return
        if self.rect.colliderect(player.collision_rect):
            if not self.recapturing:
                self.recapturing = True
                self.recapture_time = pygame.time.get_ticks()
                print(f"Recapture started at ({self.rect.x}, {self.rect.y})")
            else:
                time_held = pygame.time.get_ticks() - self.recapture_time
                if time_held >= self.recapture_duration:
                    self.captured = False
                    self.recapturing = False
                    self.recapture_time = 0
                    print(f"Flag recaptured at ({self.rect.x}, {self.rect.y})")
        else:
            if self.recapturing:
                print(f"Recapture interrupted at ({self.rect.x}, {self.rect.y})")
            self.recapturing = False
            self.recapture_time = 0

    def draw(self, surface):
        now = pygame.time.get_ticks()
        if now - self.animation_timer > self.animation_delay:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.animation_timer = now
        image = (
            self.captured_images[self.image_index]
            if self.captured
            else self.images[self.image_index]
        )
        surface.blit(image, self.rect.topleft)
        if self.recapturing:
            time_held = pygame.time.get_ticks() - self.recapture_time
            progress = min(time_held / self.recapture_duration, 1.0)
            bar_width = OBSTACLE_SIZE * progress
            bar_height = 5
            bar_rect = pygame.Rect(
                self.rect.x, self.rect.y + OBSTACLE_SIZE, bar_width, bar_height
            )
            pygame.draw.rect(surface, (0, 255, 0), bar_rect)


class TankFactory:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, OBSTACLE_SIZE, OBSTACLE_SIZE)
        self.color = (128, 128, 128)
        self.spawn_cooldown = 600
        self.cooldown_timer = 0
        self.images = []
        try:
            self.images = [
                pygame.image.load("textures/factory1.png").convert_alpha(),
                pygame.image.load("textures/factory2.png").convert_alpha(),
            ]
            self.images = [
                pygame.transform.scale(img, (OBSTACLE_SIZE, OBSTACLE_SIZE))
                for img in self.images
            ]
            for img in self.images:
                img.fill((100, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)
        except pygame.error as e:
            print(f"Error loading factory images: {e}")
            self.images = [
                pygame.Surface((OBSTACLE_SIZE, OBSTACLE_SIZE)) for _ in range(2)
            ]
            for img in self.images:
                img.fill(self.color)
        self.image_index = 0
        self.animation_timer = 0
        self.animation_delay = 400
        self.is_spawning = False

    def update(self, enemies, flags, game_level):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
        else:
            self.is_spawning = True
            self.cooldown_timer = self.spawn_cooldown
            if game_level == 1:
                # Level 1: Only non-shooting Enemy and non-shooting BaseChasingShootingEnemy
                enemy_types = [
                    (Enemy, {"direction": "random"}),
                    (
                        (BaseChasingShootingEnemy, {"flags": flags, "can_shoot": False})
                        if flags
                        else None
                    ),
                ]
            elif game_level == 2:
                # Level 2: All enemy types with improved stats
                enemy_types = [
                    (ChasingEnemy, {}),
                    (RandomShootingEnemy, {}),
                    (BaseChasingShootingEnemy, {"flags": flags}) if flags else None,
                ]
            else:  # game_level == 3
                # Level 3: No random Enemy, only advanced enemies with further improved stats
                enemy_types = [
                    (ChasingEnemy, {}),
                    (RandomShootingEnemy, {}),
                    (BaseChasingShootingEnemy, {"flags": flags}) if flags else None,
                ]
            enemy_types = [et for et in enemy_types if et is not None]
            EnemyType, kwargs = random.choice(enemy_types)
            new_enemy = EnemyType(self.rect.x, self.rect.y, level=game_level, **kwargs)
            return new_enemy
        return None

    def draw(self, surface):
        if self.is_spawning:
            now = pygame.time.get_ticks()
            if now - self.animation_timer > self.animation_delay:
                self.image_index = (self.image_index + 1) % len(self.images)
                self.animation_timer = now
                if self.image_index == 0:  # Reset spawning state after one cycle
                    self.is_spawning = False
        surface.blit(self.images[self.image_index], self.rect.topleft)
