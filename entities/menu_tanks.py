import pygame
import math
from config import COLOR_BLACK, COLOR_WHITE
from utils.logger import log
from scenes.menu_scene import *
import random

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

    def move(self):
        if self.direction == "up":
            self.y -= self.speed
        elif self.direction == "down":
            self.y += self.speed
        elif self.direction == "left":
            self.x -= self.speed
        elif self.direction == "right":
            self.x += self.speed

        # случайная смена направления
        if random.random() < 0.02:
            self.direction = random.choice(["up", "down", "left", "right"])

        # границы экрана
        self.x = max(0, min(self.x, 800 - self.width))  # assuming screen width = 800
        self.y = max(0, min(self.y, 600 - self.height)) # assuming screen height = 600

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > 1000:  # 1 выстрел в секунду
            dx, dy = 0, 0
            if self.direction == "up": dy = -5
            elif self.direction == "down": dy = 5
            elif self.direction == "left": dx = -5
            elif self.direction == "right": dx = 5
            self.shots.append([self.x + self.width // 2, self.y + self.height // 2, dx, dy])
            self.last_shot_time = now
    def shoot_at(self, target):
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > 1000:  # 1 выстрел в секунду
            dx = target.x + target.width // 2 - (self.x + self.width // 2)
            dy = target.y + target.height // 2 - (self.y + self.height // 2)
            distance = math.hypot(dx, dy)
            if distance == 0:
                distance = 1
            dx /= distance
            dy /= distance
            speed = 5
            self.shots.append([self.x + self.width // 2, self.y + self.height // 2, dx * speed, dy * speed])
            self.last_shot_time = now


    def update(self, target):
        self.move()
        self.shoot_at(target)
        for shot in self.shots:
            shot[0] += shot[2]
            shot[1] += shot[3]
        self.shots = [s for s in self.shots if 0 <= s[0] <= 800 and 0 <= s[1] <= 600]


    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        for shot in self.shots:
            pygame.draw.circle(screen, self.color, (int(shot[0]), int(shot[1])), 4)
    def check_hit(self, other):
        hit = False
        for shot in self.shots:
            if (other.x < shot[0] < other.x + other.width and
                other.y < shot[1] < other.y + other.height):
                hit = True
                self.shots.remove(shot)
        return hit
