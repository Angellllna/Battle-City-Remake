import pygame
from config import OBSTACLE_SIZE, COLOR_BLUE
from entities.enemy import Enemy, ChasingEnemy, RandomShootingEnemy, ShootingEnemy, BaseChasingShootingEnemy, FlagChasingEnemy
import random

class Obstacle:
    def __init__(self, x, y, width=OBSTACLE_SIZE, height=OBSTACLE_SIZE, color=(100, 0, 0), destructible=False, hp=1, blocks_movement=True, blocks_bullets=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.destructible = destructible
        self.hp = hp
        self.blocks_movement = blocks_movement
        self.blocks_bullets = blocks_bullets
        self.image = None
        if self.destructible:
            try:
                self.image = pygame.image.load("Battle-City-Remake/textures/brick.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, (width, height))
            except pygame.error as e:
                print(f"Error loading brick image: {e}")

    def hit(self, bullet=None):
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
        super().__init__(x, y, width=OBSTACLE_SIZE, height=OBSTACLE_SIZE, color=(150, 150, 150), destructible=False)
        try:
            self.image = pygame.image.load("Battle-City-Remake/textures/steel.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
        except pygame.error as e:
            print(f"Error loading steel image: {e}")

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect.topleft)

class WaterBlock(Obstacle):
    def __init__(self, x, y):
        super().__init__(x, y, color=(0, 255, 255), destructible=False, blocks_movement=True, blocks_bullets=False)
        self.images = []
        try:
            self.images = [
                pygame.image.load("Battle-City-Remake/textures/water1.png").convert_alpha(),
                pygame.image.load("Battle-City-Remake/textures/water2.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (self.rect.width, self.rect.height)) for img in self.images]
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
        super().__init__(x, y, color=(34, 139, 34), destructible=False, blocks_movement=False, blocks_bullets=False)
        try:
            self.image = pygame.image.load("Battle-City-Remake/textures/bush.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
        except pygame.error as e:
            print(f"Error loading bush image: {e}")

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect.topleft)

class Shield(Obstacle):
    def __init__(self, x, y):
        super().__init__(x, y, width=OBSTACLE_SIZE, height=OBSTACLE_SIZE, color=COLOR_BLUE, destructible=False, blocks_movement=False, blocks_bullets=True)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class DefendFlag:
    def __init__(self, x, y):
        self.images = []
        self.captured_images = []
        try:
            self.images = [
                pygame.image.load("Battle-City-Remake/textures/flag_GREEN1.png").convert_alpha(),
                pygame.image.load("Battle-City-Remake/textures/flag_GREEN2.png").convert_alpha()
            ]
            self.captured_images = [
                pygame.image.load("Battle-City-Remake/textures/flag_RED1.png").convert_alpha(),
                pygame.image.load("Battle-City-Remake/textures/flag_RED2.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (OBSTACLE_SIZE, OBSTACLE_SIZE)) for img in self.images]
            self.captured_images = [pygame.transform.scale(img, (OBSTACLE_SIZE, OBSTACLE_SIZE)) for img in self.captured_images]
        except pygame.error as e:
            print(f"Error loading flag images: {e}")
            self.images = [pygame.Surface((OBSTACLE_SIZE, OBSTACLE_SIZE)) for _ in range(2)]
            self.captured_images = [pygame.Surface((OBSTACLE_SIZE, OBSTACLE_SIZE)) for _ in range(2)]
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

    def check_capture(self, enemy_tanks):
        if self.captured:
            return
        for enemy in enemy_tanks:
            if self.rect.colliderect(enemy.collision_rect):
                self.captured = True
                break

    def check_recapture(self, player):
        if not self.captured:
            return
        if self.rect.colliderect(player.collision_rect):
            if not self.recapturing:
                self.recapturing = True
                self.recapture_time = pygame.time.get_ticks()
            else:
                time_held = (pygame.time.get_ticks() - self.recapture_time) / 1000
                if time_held >= 5:  # 5 seconds to recapture
                    self.captured = False
                    self.recapturing = False
                    self.recapture_time = 0
        else:
            self.recapturing = False
            self.recapture_time = 0

    def draw(self, surface):
        now = pygame.time.get_ticks()
        if now - self.animation_timer > self.animation_delay:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.animation_timer = now
        image = self.captured_images[self.image_index] if self.captured else self.images[self.image_index]
        surface.blit(image, self.rect.topleft)

class TankFactory:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, OBSTACLE_SIZE, OBSTACLE_SIZE)
        self.color = (128, 128, 128)
        self.spawn_cooldown = 300
        self.cooldown_timer = 0
        self.images = []
        try:
            self.images = [
                pygame.image.load("Battle-City-Remake/textures/factory1.png").convert_alpha(),
                pygame.image.load("Battle-City-Remake/textures/factory2.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (OBSTACLE_SIZE, OBSTACLE_SIZE)) for img in self.images]
        except pygame.error as e:
            print(f"Error loading factory images: {e}")
            self.images = [pygame.Surface((OBSTACLE_SIZE, OBSTACLE_SIZE)) for _ in range(2)]
            for img in self.images:
                img.fill(self.color)
        self.image_index = 0
        self.animation_timer = 0
        self.animation_delay = 400
        self.is_spawning = False

    def update(self, enemies, flags):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
        else:
            self.is_spawning = True
            self.cooldown_timer = self.spawn_cooldown
            enemy_types = [
                (Enemy, {"direction": "random"}),
                (ChasingEnemy, {}),
                (RandomShootingEnemy, {}),
                (BaseChasingShootingEnemy, {"flags": flags}) if flags else None
                (FlagChasingEnemy, {"flags": flags}) if flags else None
            ]
            enemy_types = [et for et in enemy_types if et is not None]
            EnemyType, kwargs = random.choice(enemy_types)
            new_enemy = EnemyType(self.rect.x, self.rect.y, **kwargs)
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