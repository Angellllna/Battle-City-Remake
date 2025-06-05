import pygame
from config import COLOR_BLACK
import config
from config import WINDOW_WIDTH, WINDOW_HEIGHT
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
        self.player = Player(380, 275)  # Центр ігрового поля
        self.obstacles = [
            # ліва і права стінки
            Obstacle(100, 50), Obstacle(100, 100), Obstacle(100, 150),
            Obstacle(100, 400), Obstacle(100, 450),
            Obstacle(100, 500), Obstacle(100, 550), Obstacle(100, 0),
    
            Obstacle(0, 210), Obstacle(0, 260), Obstacle(0, 310), Obstacle(0, 360),

            Obstacle(650, 50), Obstacle(650, 100), Obstacle(650, 150),
            Obstacle(650, 400), Obstacle(650, 450),
            Obstacle(650, 500), Obstacle(650, 550), Obstacle(650, 0),
    
            Obstacle(760, 360), Obstacle(760, 310), Obstacle(760, 260), Obstacle(760, 210),

            # центральні вертикальні блоки
            Obstacle(250, 100), Obstacle(250, 150), Obstacle(250, 200), Obstacle(250, 250),
            Obstacle(250, 300), Obstacle(250, 350), Obstacle(250, 400), Obstacle(250, 450),

            Obstacle(500, 100), Obstacle(500, 150), Obstacle(500, 200), Obstacle(500, 250),
            Obstacle(500, 300), Obstacle(500, 350), Obstacle(500, 400), Obstacle(500, 450),
    

            # верхні горизонтальні блоки
            Obstacle(350, 50), Obstacle(400, 50),
            Obstacle(350, 100), Obstacle(400, 100),
            Obstacle(350, 150), Obstacle(400, 150),

            # нижні горизонтальні блоки
            Obstacle(350, 400), Obstacle(400, 400),
            Obstacle(350, 450), Obstacle(400, 450),
            Obstacle(350, 500), Obstacle(375, 500), Obstacle(400, 500),
            Obstacle(650, 280), Obstacle(100, 280),
        ]
        self.shields = [
            Shield(250, 50),
            Shield(250, 500),
            Shield(500, 50),
            Shield(500, 500),
            ]
        self.enemies = [Enemy(200, 550, direction="vertical"), Enemy(550, 550, direction="vertical"),
                        Enemy(600, 0),Enemy(150, 550),Enemy(50, 550, direction="vertical"), Enemy(700, 550, direction="vertical")]
        self.bullets = []
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
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.player.health -= 1
                log(f"❤️ Гравець ранений! Здоров'я: {self.player.health}")
                if self.player.health <= 0:
                    log("💀 Гравець помер, переход в GameOverScene")
                    pygame.mixer.music.stop()
                    return GameOverScene(self.screen)
        if not self.enemies:
            log("🏆 Всі вороги знищені, переход в GameWinScene")
            pygame.mixer.music.stop()
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
