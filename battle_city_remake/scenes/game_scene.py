import pygame
from config import *
from entities.player import Player
from entities.obstacle import Obstacle
from entities.bullet import Bullet
from entities.enemy import Enemy
from utils.logger import log
from scenes.game_over_scene import GameOverScene


class GameScene:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 24)
        self.bullets = []
        self.next_scene = None

        self.player = Player(100, 100)
        self.obstacles = [
            Obstacle(300, 300),
            Obstacle(400, 150)
        ]
        self.enemies = [
            Enemy(200, 400, direction="horizontal"),
            Enemy(600, 100, direction="vertical")
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                log("Player pressed ESC — Game Over")
                self.next_scene = GameOverScene(self.screen)

            if event.key == pygame.K_SPACE:
                dx, dy = self.player.direction
                if dx != 0 or dy != 0:
                    bullet = Bullet(
                        self.player.rect.centerx,
                        self.player.rect.centery,
                        dx, dy
                    )
                    self.bullets.append(bullet)
                    log(f"{PLAYER_NAME} shot bullet at {dx, dy}")

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.obstacles)

        for enemy in self.enemies[:]:
            enemy.move(self.obstacles)

        self.update_bullets()
        self.check_collision_with_enemies()

        if self.next_scene:
            return self.next_scene

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.move()

            if (bullet.rect.x < 0 or bullet.rect.x > WIN_WIDTH or
                bullet.rect.y < 0 or bullet.rect.y > WIN_HEIGHT):
                self.bullets.remove(bullet)
                continue

            if any(bullet.rect.colliderect(obs.rect) for obs in self.obstacles):
                self.bullets.remove(bullet)
                log("Bullet hit a wall")
                continue

            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    self.enemies.remove(enemy)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    log("Bullet hit an enemy!")
                    break

    def check_collision_with_enemies(self):
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.player.health -= 1
                log(f"{PLAYER_NAME} hit by enemy! Health: {self.player.health}")
                self.player.rect.x, self.player.rect.y = 100, 100
                break

        if self.player.health <= 0:
            log("No health — Game Over")
            self.next_scene = GameOverScene(self.screen)

    def draw(self):
        self.screen.fill(COLOR_BLACK)

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        self.player.draw(self.screen)

        health_text = self.font.render(f"Здоров'я: {self.player.health}", True, (255, 255, 255))
        self.screen.blit(health_text, (10, 10))
