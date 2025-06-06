from entities.shield import Shield
import pygame
from config import COLOR_BLACK
from entities.player import Player
from entities.obstacle import Obstacle
from entities.bullet import Bullet
from scenes.game_win_scene import GameWinScene

class GameScene:
    def __init__(self, screen):
        self.screen = screen
        self.player = Player(100, 100)
        self.font = pygame.font.SysFont("arial", 24)
        self.bullets = []
        self.obstacles = [
            Obstacle(300, 300),
            Obstacle(400, 150)
        ]

        self.shields = [
            # Change positions ⚠️
            Shield(200, 200),
            Shield(600, 400)
        ]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                log("❌ Player pressed ESC — Game Over")
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
                    log(f"🔫 Player fired a bullet at dir {dx, dy}")


    def update(self):
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.obstacles)

        for enemy in self.enemies[:]:
            enemy.move(self.obstacles)

            # Зіткнення з щитом — знищення ворога
            for shield in self.shields:
                if enemy.rect.colliderect(shield.rect):
                    self.enemies.remove(enemy)
                    log("🛡️ Enemy destroyed by shield")
                    break

        self.update_bullets()
        self.check_collision_with_enemies()

        # Перевірка перемоги
        if len(self.enemies) == 0:
            log("🏆 All enemies defeated — PLAYER WINS")
            self.next_scene = GameWinScene(self.screen)

        if self.next_scene:
            return self.next_scene

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.move()

            if (bullet.rect.x < 0 or bullet.rect.x > WINDOW_WIDTH or
                bullet.rect.y < 0 or bullet.rect.y > WINDOW_HEIGHT):
                self.bullets.remove(bullet)
                continue

            if any(bullet.rect.colliderect(obs.rect) for obs in self.obstacles):
                self.bullets.remove(bullet)
                log("🧱 Bullet hit a wall and was destroyed")
                continue

            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    self.enemies.remove(enemy)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    log("💥 Bullet hit enemy!")
                    break

    def draw(self):
        self.screen.fill(COLOR_BLACK)

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        self.player.draw(self.screen)

        # Виведення здоров’я
        health_text = self.font.render(f"Здоров'я: {self.player.health}", True, (255, 255, 255))
        self.screen.blit(health_text, (10, 10))

        for shield in self.shields:
            shield.draw(self.screen)
