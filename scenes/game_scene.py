import pygame
from config import COLOR_BLACK
import config
from config import WINDOW_WIDTH, WINDOW_HEIGHT, OBSTACLE_SIZE, IMMORTAL_TIME, MAP1
from entities.player import Player
from entities.obstacle import Obstacle
from entities.enemy import Enemy
from entities.bullet import Bullet
from scenes.game_over_scene import GameOverScene
from scenes.game_win_scene import GameWinScene
from entities.shield import Shield
from utils.logger import log
# GameScene - основна ігрова сцена, де відбувається геймплей
class GameScene:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 24)
        self.shoot_sound = pygame.mixer.Sound("sounds\laserShoot.wav")
        self.immortal_time = 0

        tile_size = 50
        self.obstacles = []
        self.shields = []
        self.enemies = []
        for row_index, row in enumerate(MAP1):
            for col_index, cell in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if cell == "wl":
                    self.obstacles.append(Obstacle(x, y))
                elif cell == "sd":
                    self.shields.append(Shield(x, y))
                elif cell == "e1":
                    self.enemies.append(Enemy(x, y, direction="horizontal"))
                elif cell == "e2":
                    self.enemies.append(Enemy(x, y, direction="vertical"))
                elif cell == "e3":
                    self.enemies.append(Enemy(x, y, direction="chase"))
                elif cell == "pl":
                    self.player = Player(x, y)
        self.bullets = []
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("sounds/mainTheme.mp3")
            pygame.mixer.music.play(1)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet = self.player.shoot()
                self.bullets.append(bullet)
                self.shoot_sound.play()
            elif event.key == pygame.K_ESCAPE:
                log("🚪 Вихід в GameOverScene на ESC")

                return GameOverScene(self.screen)
        return None

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.obstacles)
        
        self.update_bullets()
        
        for enemy in self.enemies[:]:
            enemy.move(self.obstacles, self.player)

            # Зіткнення з щитом — знищення ворога
            for shield in self.shields:
                if enemy.rect.colliderect(shield.rect):
                    self.enemies.remove(enemy)
                    log("🛡️ Enemy destroyed by shield")
                    break

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
                    log("💥 Bullet hit enemy!")
                    break
        if self.immortal_time > 0:
            self.immortal_time -= 1
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect) and self.immortal_time <= 0:
                self.player.health -= 1
                log(f"❤️ Гравець ранений! Здоров'я: {self.player.health}")
                self.immortal_time = IMMORTAL_TIME
                if self.player.health <= 0:
                    log("💀 Гравець помер, переход в GameOverScene")
                    return GameOverScene(self.screen)
        if not self.enemies:
            log("🏆 Всі вороги знищені, переход в GameWinScene")
            return GameWinScene(self.screen)

        return None
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

    def draw(self):
        self.screen.fill(COLOR_BLACK)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        self.player.draw(self.screen)
        for shield in self.shields:
            shield.draw(self.screen)

        if self.player.health > 2:
            health_color = (0, 255, 0)  # зелений
        elif self.player.health == 2:
            health_color = (255, 255, 0)  # жовтий
        else:
            health_color = (255, 0, 0)  # червоний

        health_text = self.font.render(f"Здоров'я: {self.player.health}", True, health_color)
        self.screen.blit(health_text, (10, 10))
