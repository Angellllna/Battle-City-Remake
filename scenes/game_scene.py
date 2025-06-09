import pygame
from config import COLOR_BLACK, WINDOW_WIDTH, WINDOW_HEIGHT, IMMORTAL_TIME, MAP1, OBSTACLE_SIZE
from entities.player import Player
from entities.obstacle import Obstacle, SteelBlock, WaterBlock, BushBlock
from entities.enemy import Enemy, ChasingEnemy
from entities.bullet import Bullet, Missile
from entities.particle import Particle
from scenes.game_over_scene import GameOverScene
from scenes.game_win_scene import GameWinScene
from entities.shield import Shield
from utils.logger import log
import random

class GameScene:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 24)
        try:
            self.shoot_sound = pygame.mixer.Sound("Battle-City-Remake/sounds/laserShoot.wav")
        except pygame.error as e:
            log(f"⚠️ Failed to load shoot sound: {e}")
            self.shoot_sound = None
        self.player = Player((380, 275))
        self.immortal_time = 0
        self.particles = []

        tile_size = OBSTACLE_SIZE
        self.obstacles = []
        self.shields = []
        self.enemies = []
        self.missiles = []
        for row_index, row in enumerate(MAP1):
            for col_index, cell in enumerate(row):
                x = (col_index - 1) * tile_size
                y = (row_index - 1) * tile_size
                if cell == "wl":
                    self.obstacles.append(SteelBlock(x, y))
                elif cell == "br":
                    self.obstacles.append(Obstacle(x, y, destructible=True, hp=1))
                elif cell == "wt":
                    self.obstacles.append(WaterBlock(x, y))
                elif cell == "bu":
                    self.obstacles.append(BushBlock(x, y))
                elif cell == "sd":
                    self.shields.append(Shield(x, y))
                elif cell == "e1":
                    self.enemies.append(Enemy(x, y, direction="horizontal"))
                elif cell == "e2":
                    self.enemies.append(Enemy(x, y, direction="vertical"))
                elif cell == "e3":
                    self.enemies.append(ChasingEnemy(x, y))
                elif cell == "pl":
                    self.player = Player((x, y))
        self.bullets = []
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load("Battle-City-Remake/sounds/mainTheme.mp3")
                pygame.mixer.music.play(-1)
        except pygame.error as e:
            log(f"⚠️ Failed to load main theme: {e}")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet = self.player.shoot()
                if bullet:
                    self.bullets.append(bullet)
                    for _ in range (5):
                        self.particles.append(Particle(self.player.rect.centerx, self.player.rect.centery, "particle", self.player.direction[0] + random.uniform(-1 , 1), self.player.direction[1] + random.uniform(-1 , 1), random.randint(4, 16), (80, 80, 80)))
                    if self.shoot_sound:
                        self.shoot_sound.play()
            elif event.key == pygame.K_ESCAPE:
                pygame.mixer.stop()
                log("🚪 Exit to GameOverScene on ESC")
                return GameOverScene(self.screen)
        return None

    def update(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_w]:
            dy = -1
        elif keys[pygame.K_s]:
            dy = 1
        if keys[pygame.K_a]:
            dx = -1
        elif keys[pygame.K_d]:
            dx = 1
        self.player.move(dx, dy, self.obstacles, keys)
        maze_matrix = self.update_maze_matrix()

        for bullet in self.bullets[:]:
            bullet.move()
            if not self.screen.get_rect().contains(bullet.rect):
                self.bullets.remove(bullet)
                continue
            for obstacle in self.obstacles[:]:
                if obstacle.blocks_bullets:
                    if bullet.rect.colliderect(obstacle.rect):
                        if obstacle.hit(bullet):
                            for _ in range(5):
                                self.particles.append(Particle(obstacle.rect.centerx, obstacle.rect.centery, "particle", random.uniform(-2, 2), random.uniform(-2, 2), random.randint(4, 16), (80, 80, 80)))
                            self.obstacles.remove(obstacle)
                        for _ in range(5):
                            self.particles.append(Particle(bullet.rect.centerx, bullet.rect.centery, "particle", bullet.direction.x * -1 + random.uniform(-1, 1), bullet.direction.y * -1 + random.uniform(-1, 1), random.randint(4, 16), (240, 100, 40)))
                        self.bullets.remove(bullet)
                        log("🧱 Bullet hit obstacle")
                        break

        for missile in self.missiles[:]:
            missile.move()
            if not self.screen.get_rect().contains(missile.rect):
                self.missiles.remove(missile)
                continue
            for obstacle in self.obstacles[:]:
                if obstacle.blocks_bullets:
                    if missile.rect.colliderect(obstacle.rect):
                        if obstacle.hit(missile):
                            for _ in range(5):
                                self.particles.append(Particle(obstacle.rect.centerx, obstacle.rect.centery, "particle", random.uniform(-2, 2), random.uniform(-2, 2), random.randint(4, 16), (80, 80, 80)))
                            self.obstacles.remove(obstacle)
                        for _ in range(5):
                            self.particles.append(Particle(missile.rect.centerx, missile.rect.centery, "particle", missile.direction.x * -1 + random.uniform(-1, 1), missile.direction.y * -1 + random.uniform(-1, 1), random.randint(4, 16), (240, 100, 40)))
                        self.missiles.remove(missile)
                        log("🧱 Missile hit obstacle")
                        break
            for shield in self.shields:
                if missile.rect.colliderect(shield.rect):
                    for _ in range (5):
                        self.particles.append(Particle(shield.rect.centerx, shield.rect.centery, "particle", random.uniform(-2 , 2), random.uniform(-2 , 2), random.randint(4, 16), (20, 60, 240)))
                    for _ in range (5):
                        self.particles.append(Particle(missile.rect.centerx, missile.rect.centery, "particle", missile.direction.x * -1 + random.uniform(-1 , 1), missile.direction.y * -1 + random.uniform(-1 , 1), random.randint(4, 16), (240, 100, 40)))
                    self.shields.remove(shield)
                    self.missiles.remove(missile)
                    log("🛡️ Missile hit shield")
                    break
            if missile.rect.colliderect(self.player.rect) and self.immortal_time <= 0:
                self.player.health -= 1
                log(f"🚀 Player hit by missile! Health: {self.player.health}")
                self.immortal_time = IMMORTAL_TIME
                for _ in range (5):
                    self.particles.append(Particle(missile.rect.centerx, missile.rect.centery, "particle", missile.direction.x * -1 + random.uniform(-1 , 1), missile.direction.y * -1 + random.uniform(-1 , 1), random.randint(4, 16), (240, 100, 40)))
                self.missiles.remove(missile)
                if self.player.health <= 0:
                    log("💀 Player died, switching to GameOverScene")
                    pygame.mixer.stop()
                    return GameOverScene(self.screen)

        for enemy in self.enemies[:]:
            if isinstance(enemy, ChasingEnemy):
                maze_matrix = self.update_maze_matrix()
                enemy.obstacles = self.obstacles
                missile = enemy.update(self.player, maze_matrix, self.obstacles)
                if missile:
                    self.missiles.append(missile)
                    if self.shoot_sound:
                        self.shoot_sound.play()
            else:
                enemy.move(self.obstacles)

            for shield in self.shields:
                if enemy.rect.colliderect(shield.rect):
                    self.enemies.remove(enemy)
                    for _ in range (5):
                        self.particles.append(Particle(enemy.rect.centerx, enemy.rect.centery, "particle", random.uniform(-2 , 2), random.uniform(-2 , 2), random.randint(4, 16), (240, 100, 40)))
                        self.particles.append(Particle(enemy.rect.centerx, enemy.rect.centery, "particle", random.uniform(-1 , 1), random.uniform(-1 , 1), random.randint(8, 24), (40, 40, 40)))
                    log("🛡️ Enemy destroyed by shield")
                    break

            for bullet in self.bullets[:]:
                if bullet.rect.colliderect(enemy.rect):
                    for _ in range (5):
                        self.particles.append(Particle(bullet.rect.centerx, bullet.rect.centery, "particle", bullet.direction.x * -1 + random.uniform(-1 , 1), bullet.direction.y * -1 + random.uniform(-1 , 1), random.randint(4, 16), (random.randint(90, 170), random.randint(0, 40), random.randint(0, 10))))
                    self.enemies.remove(enemy)
                    self.bullets.remove(bullet)
                    log("💥 Bullet hit enemy!")
                    break

            if self.player.rect.colliderect(enemy.rect) and self.immortal_time <= 0:
                self.player.health -= 1
                log(f"❤️ Player hit by enemy! Health: {self.player.health}")
                self.immortal_time = IMMORTAL_TIME
                for _ in range (5):
                    self.particles.append(Particle(self.player.rect.centerx, self.player.rect.centery, "particle", random.uniform(-2, 2), random.uniform(-2, 2), random.randint(4, 16), (random.randint(90, 170), random.randint(0, 40), random.randint(0, 10))))
                if self.player.health <= 0:
                    log("💀 Player died, switching to GameOverScene")
                    pygame.mixer.stop()
                    return GameOverScene(self.screen)

        for particle in self.particles[:]:
            particle.move()
            if particle.rect.w <= 3 or particle.rect.h <= 3:
                self.particles.remove(particle)

        if self.immortal_time > 0:
            self.immortal_time -= 1

        if not self.enemies:
            log("🏆 All enemies defeated, switching to GameWinScene")
            pygame.mixer.stop()
            return GameWinScene(self.screen)

        return None

    def draw(self):
        self.screen.fill(COLOR_BLACK)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        for shield in self.shields:
            shield.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for missile in self.missiles:
            missile.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)
        self.player.draw(self.screen)

        health_color = (0, 255, 0) if self.player.health > 2 else (255, 255, 0) if self.player.health == 2 else (255, 0, 0)
        health_text = self.font.render(f"Health: {self.player.health}", True, health_color)
        self.screen.blit(health_text, (10, 10))

    def update_maze_matrix(self):
        tile_size = OBSTACLE_SIZE
        rows, cols = len(MAP1), len(MAP1[0])
        maze_matrix = [[0 for _ in range(cols)] for _ in range(rows)]
        for obstacle in self.obstacles:
            if obstacle.blocks_movement:
                row = obstacle.rect.centery // tile_size
                col = obstacle.rect.centerx // tile_size
                if 0 <= row < rows and 0 <= col < cols:
                    maze_matrix[row][col] = 1
        return maze_matrix