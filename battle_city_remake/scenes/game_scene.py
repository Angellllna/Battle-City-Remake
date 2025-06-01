import pygame
from config import *
from entities.player import Player
from entities.obstacle import Obstacle
from entities.bullet import Bullet
from scenes.game_over_scene import GameOverScene
from entities.enemy import *
from utils.logger import any_error_logger, log

class GameScene:
    def __init__(self, screen):
        self.bullets = []
        self.font = pygame.font.SysFont("arial", 24)
        self.screen = screen
        self.player = Player(100, 100)  # Початкова позиція
        self.obstacles = [
            Obstacle(300, 300),
            Obstacle(400, 150)
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
                    log(f"{PLAYER_NAME} has shot enemy with bullet at {dx, dy}!")

    def update(self):
        def update(self):
            keys = pygame.key.get_pressed()
            self.player.move(keys, self.obstacles)

            for enemy in self.enemies:
                enemy.move(self.obstacles)

            self.update_bullets()
            self.check_collision_with_enemies()

            if self.next_scene:
                return self.next_scene
            
    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.move()

            # Вийшла за межі
            if (bullet.rect.x < 0 or bullet.rect.x > WIN_WIDTH or
                bullet.rect.y < 0 or bullet.rect.y > WIN_HEIGHT):
                self.bullets.remove(bullet)
                continue

            # Влучила в перешкоду
            if any(bullet.rect.colliderect(obs.rect) for obs in self.obstacles):
                self.bullets.remove(bullet)
                log(f"{PLAYER_NAME}'s bullet hit a wall and was destroyed")
                continue

            # Влучила у ворога
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    self.enemies.remove(enemy)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    log(f"{PLAYER_NAME}'s bullet hit enemy!")
                    break


    def draw(self):
            self.screen.fill(BLACK)

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