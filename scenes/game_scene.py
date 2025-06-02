import pygame
from config import COLOR_BLACK
from entities.player import Player
from entities.obstacle import Obstacle
from entities.enemy import Enemy
from entities.bullet import Bullet
from scenes.game_over_scene import GameOverScene
from scenes.game_win_scene import GameWinScene
from utils.logger import log

class GameScene:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 24)
        self.player = Player(100, 100)
        self.obstacles = [Obstacle(300, 300), Obstacle(400, 150)]
        self.enemies = [Enemy(200, 200), Enemy(500, 400, direction="vertical")]
        self.bullets = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet = self.player.shoot()
                self.bullets.append(bullet)
            elif event.key == pygame.K_ESCAPE:
                log("🚪 Вихід в GameOverScene на ESC")
                return GameOverScene(self.screen)
        return None

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.obstacles)

        for enemy in self.enemies:
            enemy.move(self.obstacles)

        for bullet in self.bullets[:]:
            bullet.move()
            if not self.screen.get_rect().colliderect(bullet.rect):
                self.bullets.remove(bullet)
                continue
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    self.enemies.remove(enemy)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.player.health -= 1
                log(f"❤️ Гравець ранений! Здоров'я: {self.player.health}")
                if self.player.health <= 0:
                    log("💀 Гравець помер, переход в GameOverScene")
                    return GameOverScene(self.screen)

        if not self.enemies:
            log("🏆 Всі вороги знищені, переход в GameWinScene")
            return GameWinScene(self.screen)

        return None

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
