import os
import random
import pygame
import math
from entities.bullet import Bullet
from config import COLOR_BLUE, OBSTACLE_SIZE, PLAYER_SIZE
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
                self.image = pygame.image.load(
                    os.path.join("textures", "brick.png")
                ).convert_alpha()
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
                if self.segments[key] and bullet and bullet.rect.colliderect(seg_rect):
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
            self.image = pygame.image.load(
                os.path.join("textures", "steel.png")
            ).convert_alpha()
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
                pygame.image.load(
                    os.path.join("textures", "water1.png")
                ).convert_alpha(),
                pygame.image.load(
                    os.path.join("textures", "water2.png")
                ).convert_alpha(),
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

SHIELD_TEXTURES = [
    os.path.join("textures", "shield1.png"),
    os.path.join("textures", "shield2.png"),
    os.path.join("textures", "shield3.png"),
    os.path.join("textures", "shield4.png"),
]

class Shield(Obstacle):
    def __init__(self, x, y, move_direction=None):
        super().__init__(
            x,
            y,
            width=OBSTACLE_SIZE,
            height=OBSTACLE_SIZE,
            color=(0, 255, 255),
            destructible=True,
            hp=3,
            blocks_movement=False,
            blocks_bullets=True,
        )
        self.health = 3  # Initialize shield with 3 HP

        self.images = [
            pygame.image.load(texture).convert_alpha() for texture in SHIELD_TEXTURES
        ]
        self.images = [
            pygame.transform.scale(img, (self.rect.width, self.rect.height))
            for img in self.images
        ]
        for img in self.images:
            img.fill((0, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)

        self.SPEED = 2

        self.image_index = 0
        self.animation_timer = 0
        self.animation_delay = 100

        # Рух щита
        self.move_direction = move_direction
        self.direction_vector = self._get_direction_vector(move_direction)
        self.initial_x = x
        self.initial_y = y
        self.move_distance = 0
        self.max_move_distance = 100
        self.moving_forward = True

    def _get_direction_vector(self, direction):
        directions = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        return directions.get(direction, (0, -1))

    def hit(self, bullet=None):
        if self.destructible:
            self.health -= 1
            print(f"Shield hit! Health: {self.health}")
            return self.health <= 0  # Return True if shield is destroyed
        return False

    def update(self):
        if self.move_direction != None:
            dx = self.direction_vector[0] * self.SPEED
            dy = self.direction_vector[1] * self.SPEED

            if not self.moving_forward:
                dx = -dx
                dy = -dy

            self.rect.x += dx
            self.rect.y += dy
            self.move_distance += self.SPEED

            if self.move_distance >= self.max_move_distance:
                self.moving_forward = not self.moving_forward
                self.move_distance = 0

    def draw(self, surface):
        self.update()

        now = pygame.time.get_ticks()
        if now - self.animation_timer > self.animation_delay:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.animation_timer = now

        surface.blit(self.images[self.image_index], self.rect.topleft)

class DefendFlag:
    def __init__(self, x, y):
        self.images = []
        self.captured_images = []
        try:
            self.images = [
                pygame.image.load(
                    os.path.join("textures", "flag_GREEN1.png")
                ).convert_alpha(),
                pygame.image.load(
                    os.path.join("textures", "flag_GREEN2.png")
                ).convert_alpha(),
            ]
            self.captured_images = [
                pygame.image.load(
                    os.path.join("textures", "flag_RED1.png")
                ).convert_alpha(),
                pygame.image.load(
                    os.path.join("textures", "flag_RED2.png")
                ).convert_alpha(),
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
        self.animation_delay = 400  # мс

        self.rect = self.images[0].get_rect(topleft=(x, y))

        self.captured = False

        self.recapture_start = 0
        self.recapturing = False
        self.recapture_duration = 5000  # 5 seconds in milliseconds

        self.font = pygame.font.SysFont("arial", 16)
        self.blink_toggle = False  # для перемикання між сірим і зеленим

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
                self.recapture_start = pygame.time.get_ticks()
                print(f"Recapture started at ({self.rect.x}, {self.rect.y})")
            else:
                time_held = pygame.time.get_ticks() - self.recapture_start
                if time_held >= self.recapture_duration:
                    self.captured = False
                    self.recapturing = False
                    self.recapture_start = 0
                    print(f"Flag recaptured at ({self.rect.x}, {self.rect.y})")
        else:
            if self.recapturing:
                print(f"Recapture interrupted at ({self.rect.x}, {self.rect.y})")
            self.recapturing = False
            self.recapture_start = 0

    def draw(self, surface):
        now = pygame.time.get_ticks()

        if now - self.animation_timer > self.animation_delay:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.animation_timer = now
            self.blink_toggle = not self.blink_toggle

        if not self.recapturing and self.captured:
            image = self.captured_images[self.image_index]
        elif self.recapturing and self.captured and not self.blink_toggle:
            image = self.captured_images[self.image_index]
        else:
            image = self.images[self.image_index]

        surface.blit(image, self.rect.topleft)

        if self.recapturing and self.captured:
            time_held = pygame.time.get_ticks() - self.recapture_start
            progress = min(time_held / self.recapture_duration, 1.0)
            bar_width = OBSTACLE_SIZE * progress
            bar_height = 5
            bar_rect = pygame.Rect(
                self.rect.x, self.rect.y + OBSTACLE_SIZE - bar_height, bar_width, bar_height
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
                pygame.image.load(
                    os.path.join("textures", "factory1.png")
                ).convert_alpha(),
                pygame.image.load(
                    os.path.join("textures", "factory2.png")
                ).convert_alpha(),
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

class Turret(Obstacle):
    def __init__(self, x, y):
        super().__init__(
            x, y,
            width=OBSTACLE_SIZE,
            height=OBSTACLE_SIZE,
            color=(255, 255, 0),
            destructible=True,
            hp=3,
            blocks_movement=False,
            blocks_bullets=True,
        )
        self.x = self.rect.x
        self.y = self.rect.y
        self.collision_rect = pygame.Rect(x, y, OBSTACLE_SIZE, OBSTACLE_SIZE)
        try:
            self.image = pygame.image.load(os.path.join("textures", "turret.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
            self.image.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
        except pygame.error as e:
            print(f"Error loading turret image: {e}")
            self.image = pygame.Surface((self.rect.width, self.rect.height))
            self.image.fill(self.color)

        self.image = self.image.copy()
        self.shoot_cooldown = 60
        self.cooldown_timer = 0
        self.damage = 1
        self.health = 3  # Add health attribute

        self.target_angle = 0
        self.rotation_speed = 10  # швидкість обертання
        self.current_angle = 0

    def hit(self, bullet=None):
        if self.destructible:
            self.health -= 1
            print(f"Turret hit! Health: {self.health}")
            return self.health <= 0  # Return True if turret is destroyed
        return False

    def update(self, enemies, bullets):
        self.x = self.rect.x
        self.y = self.rect.y
        self.collision_rect.x = self.x
        self.collision_rect.y = self.y
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
        else:
            target = self.find_target(enemies)
            if target:
                dx = (target.x + PLAYER_SIZE / 2) - (self.rect.centerx)
                dy = (target.y + PLAYER_SIZE / 2) - (self.rect.centery)
                direction = pygame.Vector2(dx, dy)
                if direction.length() > 0:
                    self.target_angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90
                    bullet = Bullet(self.rect.centerx, self.rect.centery, direction.normalize(), source=self)
                    bullets.append(bullet)
                    self.cooldown_timer = self.shoot_cooldown

        # плавне обертання
        self.rotate_toward_target()

    def rotate_toward_target(self):
        diff = (self.target_angle - self.current_angle + 360) % 360
        if diff > 180:
            diff -= 360
        if abs(diff) < self.rotation_speed:
            self.current_angle = self.target_angle
        else:
            self.current_angle += self.rotation_speed * (1 if diff > 0 else -1)
            self.current_angle %= 360

    def find_target(self, enemies):
        for enemy in enemies:
            if self.collision_rect.colliderect(enemy.collision_rect.inflate(300, 300)):
                return enemy
        return None

    def draw(self, surface):
        rotated_image = pygame.transform.rotate(self.image, self.current_angle)
        rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, rect.topleft)