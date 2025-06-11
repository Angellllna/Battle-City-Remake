import pygame
import math
from entities.bullet import Bullet
from config import PLAYER_SIZE, PLAYER_SPEED, PLAYER_HEALTH

class Player:
    def __init__(self, position):
        self.x = float(position[0])
        self.y = float(position[1])
        self.collision_rect = pygame.Rect(int(self.x), int(self.y), PLAYER_SIZE, PLAYER_SIZE)
        self.base_speed = PLAYER_SPEED
        self.speed = self.base_speed
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_HEALTH
        self.bullets = []
        self.direction = pygame.Vector2(0, -1)
        self.damage = 1
        self.shoot_cooldown = 30
        self.cooldown_timer = 0
        self.upgrades = {"speed": 0, "health": 0, "damage": 0, "fire_rate": 0}
        try:
            self.images = [
                pygame.image.load("textures/tank111.png").convert_alpha(),
                pygame.image.load("textures/tank112.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]
        except pygame.error as e:
            print(f"Error loading tank images: {e}")
            self.images = [pygame.Surface((PLAYER_SIZE, PLAYER_SIZE)) for _ in range(2)]
            for img in self.images:
                img.fill((0, 255, 0))
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.animation_timer = 0
        self.animation_delay = 200
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
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            new_rect = pygame.Rect(int(new_x), int(new_y), PLAYER_SIZE, PLAYER_SIZE)
            for obstacle in obstacles:
                if obstacle.blocks_movement:
                    if new_rect.colliderect(obstacle.rect):
                        new_rect_x = pygame.Rect(int(self.x + dx * self.speed), int(self.y), PLAYER_SIZE, PLAYER_SIZE)
                        new_rect_y = pygame.Rect(int(self.x), int(self.y + dy * self.speed), PLAYER_SIZE, PLAYER_SIZE)
                        can_move_x = True
                        can_move_y = True
                        for obs in obstacles:
                            if obs.blocks_movement:
                                if new_rect_x.colliderect(obs.rect):
                                    can_move_x = False
                                if new_rect_y.colliderect(obs.rect):
                                    can_move_y = False
                        if can_move_x:
                            self.x += dx * self.speed
                        elif can_move_y:
                            self.y += dy * self.speed
                        self.collision_rect = pygame.Rect(int(self.x), int(self.y), PLAYER_SIZE, PLAYER_SIZE)
                        return
            self.x = new_x
            self.y = new_y
            self.collision_rect = pygame.Rect(int(self.x), int(self.y), PLAYER_SIZE, PLAYER_SIZE)
        self.update()

    def get_angle_from_direction(self, direction):
        angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90
        return angle % 360

    def collect_part(self, part):
        if part.type != "repair" and self.upgrades[part.type] <= 11:
            self.upgrades[part.type] += 1
        if part.type == "speed" and self.upgrades[part.type] <= 11:
            self.speed = self.base_speed * (1.0 + 0.1 * self.upgrades["speed"])
        elif part.type == "health":
            if self.upgrades[part.type] <= 11:
                self.max_health += 2
            self.health = min(self.health + 3, self.max_health)
        elif part.type == "damage" and self.upgrades[part.type] <= 11:
            self.damage += 0.5
        elif part.type == "fire_rate" and self.upgrades[part.type] <= 11:
            self.shoot_cooldown = max(10, self.shoot_cooldown - 5)
        elif part.type == "repair":
            self.health = self.max_health
        print(f"Collected {part.type} part! Upgrades: {self.upgrades}")

    def shoot(self):
        if self.direction.length_squared() == 0 or self.cooldown_timer > 0:
            return None
        self.cooldown_timer = self.shoot_cooldown
        # Центр танка
        center_x = self.x + PLAYER_SIZE / 2 - 5
        center_y = self.y + PLAYER_SIZE / 2 - 5
        # Зміщення до дула (припускаємо, що дуло на відстані PLAYER_SIZE / 2 від центра)
        offset = PLAYER_SIZE / 2
        # Обчислюємо позицію дула
        bullet_x = center_x + self.direction.x * offset
        bullet_y = center_y + self.direction.y * offset
        return Bullet(bullet_x, bullet_y, self.direction.normalize(), damage=self.damage)

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
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1

    def draw(self, surface):

        if self.upgrades["health"] >= 5:
            self.images = [
                pygame.image.load("textures/tank211.png").convert_alpha(),
                pygame.image.load("textures/tank212.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]

        if self.upgrades["speed"] >= 5:
            self.images = [
                pygame.image.load("textures/tank121.png").convert_alpha(),
                pygame.image.load("textures/tank122.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]

        if self.upgrades["speed"] >= 5 and self.upgrades["damage"] >= 5:
            self.images = [
                pygame.image.load("textures/tank321.png").convert_alpha(),
                pygame.image.load("textures/tank322.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]
        
        if self.upgrades["speed"] >= 10:
            self.images = [
                pygame.image.load("textures/tank131.png").convert_alpha(),
                pygame.image.load("textures/tank132.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]


        if self.upgrades["health"] >= 5 and self.upgrades["damage"] >= 5:
            self.images = [
                pygame.image.load("textures/tank221.png").convert_alpha(),
                pygame.image.load("textures/tank222.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]

        if self.upgrades["health"] >= 10:
            self.images = [
                pygame.image.load("textures/tank231.png").convert_alpha(),
                pygame.image.load("textures/tank232.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]

        if self.upgrades["health"] >= 10 and self.upgrades["damage"] >= 10 and self.upgrades["speed"] >= 10:
            self.images = [
                pygame.image.load("textures/tank331.png").convert_alpha(),
                pygame.image.load("textures/tank332.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]



        img_rect = self.image.get_rect(center=(int(self.x + PLAYER_SIZE / 2), int(self.y + PLAYER_SIZE / 2)))
        surface.blit(self.image, img_rect.topleft)
        for bullet in self.bullets:
            bullet.draw(surface)