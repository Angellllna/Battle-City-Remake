import pygame
import time
from config import COLOR_BLACK
from entities.flag import *
from entities.defend_flag import *
import config
from config import WINDOW_WIDTH, WINDOW_HEIGHT, MAP1
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
        self.last_hit_time = 0
        self.invulnerability_duration = 1.5  # Секунди невразливості після удару
        self.font = pygame.font.SysFont("arial", 24)
        self.shoot_sound = pygame.mixer.Sound("sounds\laserShoot.wav")
        tile_size = 50
        self.captured_flags = 0
        self.player = Player(380, 280)
        self.obstacles = []
        self.shields = []
        self.enemies = [Enemy(750, 275, direction="horizontal"),
                        Enemy(10, 275, direction="horizontal"),]  
        self.bullets = []
        self.flags = [Flag(380, 560), Flag(380, 60)]  # Два прапори для захоплення
        #self.defend_flag = DefendFlag(380, 560)
        for row_index, row in enumerate(MAP1):
            for col_index, cell in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if cell == "wl":
                    self.obstacles.append(Obstacle(x, y))
                elif cell == "sd":
                    self.shields.append(Shield(x, y))
                elif cell == "e1":
                    self.enemies.append(Enemy(x, y, direction="vertical"))
                elif cell == "e2":
                    self.enemies.append(Enemy(x, y, direction="vertical"))
                elif cell == "e3":
                    self.enemies.append(Enemy(x, y, direction="chase"))
                elif cell == "pl":
                    self.player = Player(x, y)
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load("sounds/mainTheme.mp3")
            pygame.mixer.music.play(-1)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet = self.player.shoot()
                self.bullets.append(bullet)
                self.shoot_sound.play()
            elif event.key == pygame.K_ESCAPE:
                log("🚪 Вихід в GameOverScene на ESC")
                pygame.mixer.music.stop()
                return GameOverScene(self.screen)
        return None

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.obstacles)
        
        self.update_bullets()
        
        for enemy in self.enemies[:]:
            enemy.move(self.obstacles)

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
        current_time = time.time()
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                if current_time - self.last_hit_time >= self.invulnerability_duration:
                    self.player.health -= 1
                    self.last_hit_time = current_time
                    log(f"❤️ Гравець ранений! Здоров'я: {self.player.health}")
                    if self.player.health <= 0:
                        log("💀 Гравець помер, переход в GameOverScene")
                        pygame.mixer.music.stop()
                        return GameOverScene(self.screen)
        if not self.enemies:
            log("🏆 Всі вороги знищені, переход в GameWinScene")
            pygame.mixer.music.stop()
            return GameWinScene(self.screen)
        for flag in self.flags:
            flag.check_capture(self.player)
            if flag.captured and not hasattr(flag, "counted"):
                self.captured_flags += 1
                flag.counted = True
                log(f"🚩 Прапор захоплено! Загалом: {self.captured_flags}")
        if all(flag.captured for flag in self.flags):
            log("🏁 Усі прапори захоплено! Перемога!")
            pygame.mixer.music.stop()
            return GameWinScene(self.screen)
        # Оновлення прапорів
        for flag in self.flags:
            flag.check_capture(self.player)

        #self.defend_flag.check_capture(self.enemies)

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
        for flag in self.flags:
            flag.draw(self.screen)

        #self.defend_flag.draw(self.screen)

        if self.player.health > 2:
            health_color = (0, 255, 0)  # зелений
        elif self.player.health == 2:
            health_color = (255, 255, 0)  # жовтий
        else:
            health_color = (255, 0, 0)  # червоний

        health_text = self.font.render(f"Здоров'я: {self.player.health}", True, health_color)
        self.screen.blit(health_text, (10, 10))
        flags_text = self.font.render(f"Захоплено прапорів: {self.captured_flags}", True, (0,255,0))
        self.screen.blit(flags_text, (10, 40))
