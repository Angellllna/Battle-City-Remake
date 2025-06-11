import os
import random

import pygame

from config import (
    COLOR_BLACK,
    IMMORTAL_TIME,
    MAP1,
    OBSTACLE_SIZE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from entities.bullet import Bullet, Missile
from entities.enemy import (
    BaseChasingShootingEnemy,
    ChasingEnemy,
    Enemy,
    FlagChasingEnemy,
    RandomShootingEnemy,
    ShootingEnemy,
)
from entities.obstacle import (
    BushBlock,
    DefendFlag,
    Obstacle,
    Shield,
    SteelBlock,
    TankFactory,
    WaterBlock,
)
from entities.particle import Particle
from entities.player import Player
from scenes.game_over_scene import GameOverScene
from utils.logger import log


class GameScene:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 24, bold=True)
        try:
            self.shoot_sound = pygame.mixer.Sound(
                os.path.join("sounds", "laserShoot.wav")
            )
        except pygame.error as e:
            log(f"⚠️ Failed to load shoot sound: {e}")
            self.shoot_sound = None

        self.immortal_time = 0
        self.particles = []
        self.flags = []
        self.tank_factories = []
        self.destroyed_enemies = 0
        self.start_time = pygame.time.get_ticks()

        tile_size = OBSTACLE_SIZE
        self.obstacles = []
        self.shields = []
        self.enemies = []
        self.missiles = []
        for row_index, row in enumerate(MAP1):
            for col_index, cell in enumerate(row):
                x = (col_index - 1) * tile_size
                y = (row_index - 1) * tile_size
                if cell == "fl":
                    self.flags.append(DefendFlag(x, y))

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
                elif cell == "pl":
                    self.player = Player((x, y))
                elif cell == "sd":
                    self.shields.append(Shield(x, y))
                elif cell == "tf":
                    self.tank_factories.append(TankFactory(x, y))
                elif cell == "e1":
                    self.enemies.append(Enemy(x, y, direction="horizontal"))
                elif cell == "e2":
                    self.enemies.append(Enemy(x, y, direction="vertical"))
                elif cell == "e3":
                    self.enemies.append(ChasingEnemy(x, y))
                elif cell == "e4":
                    self.enemies.append(Enemy(x, y, direction="random"))
                elif cell == "e5":
                    self.enemies.append(RandomShootingEnemy(x, y))
                elif cell == "e6":
                    self.enemies.append(ShootingEnemy(x, y, direction="horizontal"))
                elif cell == "e7":
                    self.enemies.append(ShootingEnemy(x, y, direction="vertical"))
                elif cell == "e8":
                    if self.flags:
                        self.enemies.append(BaseChasingShootingEnemy(x, y, self.flags))
                    else:
                        log("⚠️ Flags not defined before e8 enemy placement")
                        self.enemies.append(Enemy(x, y, direction="random"))
                elif cell == "e9":
                    if self.flags:
                        self.enemies.append(FlagChasingEnemy(x, y, self.flags))
                    else:
                        log("⚠️ Flags not defined before e9 enemy placement")
                        self.enemies.append(Enemy(x, y, direction="random"))
        self.bullets = []

    def get_game_level(self):
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        if elapsed_time < 60:
            return 1
        elif elapsed_time < 120:
            return 2
        else:
            return 3

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet = self.player.shoot()
                if bullet:
                    self.bullets.append(bullet)
                    for _ in range(5):
                        self.particles.append(
                            Particle(
                                self.player.collision_rect.centerx,
                                self.player.collision_rect.centery,
                                "particle",
                                self.player.direction[0] + random.uniform(-1, 1),
                                self.player.direction[1] + random.uniform(-1, 1),
                                random.randint(4, 16),
                                (80, 80, 80),
                            )
                        )
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

        all_flags_captured = all(flag.captured for flag in self.flags)
        for flag in self.flags:
            flag.check_capture(self.enemies)
            flag.check_recapture(self.player)
        if all_flags_captured:
            log("🚩 All flags captured, switching to GameOverScene")
            pygame.mixer.stop()
            return GameOverScene(self.screen)

        game_level = self.get_game_level()
        for factory in self.tank_factories:
            new_enemy = factory.update(self.enemies, self.flags, game_level)
            if new_enemy:
                self.enemies.append(new_enemy)
                log(
                    f"🏭 Factory spawned new enemy: {new_enemy.__class__.__name__} (Level {game_level})"
                )

        for bullet in self.bullets[:]:
            bullet.move()
            if not self.screen.get_rect().contains(bullet.rect):
                self.bullets.remove(bullet)
                continue
            for obstacle in self.obstacles[:]:
                if obstacle.blocks_bullets:
                    rects_to_check = [obstacle.rect]

                    if hasattr(obstacle, "get_collision_rects"):
                        rects_to_check = obstacle.get_collision_rects()

                    collided = False
                    for rect in rects_to_check:
                        if bullet.rect.colliderect(rect):
                            collided = True
                            break

                    if collided:
                        if obstacle.hit(bullet):
                            # for _ in range(5):
                            #     self.particles.append(
                            #         Particle(
                            #             obstacle.rect.centerx,
                            #             obstacle.rect.centery,
                            #             "particle",
                            #             random.uniform(-2, 2),
                            #             random.uniform(-2, 2),
                            #             random.randint(4, 16),
                            #             (80, 80, 80),
                            #         )
                            #     )
                            self.obstacles.remove(obstacle)
                        # for _ in range(5):
                        #     self.particles.append(
                        #         Particle(
                        #             bullet.rect.centerx,
                        #             bullet.rect.centery,
                        #             "particle",
                        #             bullet.direction.x * -1 + random.uniform(-1, 1),
                        #             bullet.direction.y * -1 + random.uniform(-1, 1),
                        #             random.randint(4, 16),
                        #             (240, 100, 40),
                        #         )
                        #     )
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
                                self.particles.append(
                                    Particle(
                                        obstacle.rect.centerx,
                                        obstacle.rect.centery,
                                        "particle",
                                        random.uniform(-2, 2),
                                        random.uniform(-2, 2),
                                        random.randint(4, 16),
                                        (80, 80, 80),
                                    )
                                )
                            self.obstacles.remove(obstacle)
                        for _ in range(5):
                            self.particles.append(
                                Particle(
                                    missile.rect.centerx,
                                    missile.rect.centery,
                                    "particle",
                                    missile.direction.x * -1 + random.uniform(-1, 1),
                                    missile.direction.y * -1 + random.uniform(-1, 1),
                                    random.randint(4, 16),
                                    (240, 100, 40),
                                )
                            )
                        self.missiles.remove(missile)
                        log("🧱 Missile hit obstacle")
                        break
            else:
                for shield in self.shields:
                    if missile.rect.colliderect(shield.rect):
                        for _ in range(5):
                            self.particles.append(
                                Particle(
                                    shield.rect.centerx,
                                    shield.rect.centery,
                                    "particle",
                                    random.uniform(-2, 2),
                                    random.uniform(-2, 2),
                                    random.randint(4, 16),
                                    (20, 60, 240),
                                )
                            )
                        for _ in range(5):
                            self.particles.append(
                                Particle(
                                    missile.rect.centerx,
                                    missile.rect.centery,
                                    "particle",
                                    missile.direction.x * -1 + random.uniform(-1, 1),
                                    missile.direction.y * -1 + random.uniform(-1, 1),
                                    random.randint(4, 16),
                                    (240, 100, 40),
                                )
                            )
                        self.shields.remove(shield)
                        self.missiles.remove(missile)
                        log("🛡️ Missile hit shield")
                        break
                else:
                    if (
                        missile.rect.colliderect(self.player.collision_rect)
                        and self.immortal_time <= 0
                    ):
                        self.player.health -= missile.damage
                        log(f"🚀 Player hit by missile! Health: {self.player.health}")
                        self.immortal_time = IMMORTAL_TIME
                        for _ in range(5):
                            self.particles.append(
                                Particle(
                                    missile.rect.centerx,
                                    missile.rect.centery,
                                    "particle",
                                    missile.direction.x * -1 + random.uniform(-1, 1),
                                    missile.direction.y * -1 + random.uniform(-1, 1),
                                    random.randint(4, 16),
                                    (240, 100, 40),
                                )
                            )
                        self.missiles.remove(missile)
                        if self.player.health <= 0:
                            log("💀 Player died, switching to GameOverScene")
                            pygame.mixer.stop()
                            return GameOverScene(self.screen)

        for enemy in self.enemies[:]:
            if isinstance(
                enemy,
                (
                    ChasingEnemy,
                    RandomShootingEnemy,
                    ShootingEnemy,
                    BaseChasingShootingEnemy,
                ),
            ):
                maze_matrix = self.update_maze_matrix()
                missile = enemy.update(self.player, maze_matrix, self.obstacles)
                if missile:
                    self.missiles.append(missile)
                    if self.shoot_sound:
                        self.shoot_sound.play()
            elif isinstance(enemy, FlagChasingEnemy):
                maze_matrix = self.update_maze_matrix()
                enemy.update(self.player, maze_matrix, self.obstacles)
            else:
                enemy.move(self.obstacles)
            for shield in self.shields:
                if enemy.collision_rect.colliderect(shield.rect):
                    self.enemies.remove(enemy)
                    self.destroyed_enemies += 1
                    for _ in range(5):
                        self.particles.append(
                            Particle(
                                enemy.collision_rect.centerx,
                                enemy.collision_rect.centery,
                                "particle",
                                random.uniform(-2, 2),
                                random.uniform(-2, 2),
                                random.randint(4, 16),
                                (240, 100, 40),
                            )
                        )
                        self.particles.append(
                            Particle(
                                enemy.collision_rect.centerx,
                                enemy.collision_rect.centery,
                                "particle",
                                random.uniform(-1, 1),
                                random.uniform(-1, 1),
                                random.randint(8, 24),
                                (40, 40, 40),
                            )
                        )
                    log(
                        f"🛡️ Enemy destroyed by shield. Total destroyed: {self.destroyed_enemies}"
                    )
                    break
            for bullet in self.bullets[:]:
                if bullet.rect.colliderect(enemy.collision_rect):
                    if enemy.hit():
                        for _ in range(5):
                            self.particles.append(
                                Particle(
                                    bullet.rect.centerx,
                                    bullet.rect.centery,
                                    "particle",
                                    bullet.direction.x * -1 + random.uniform(-1, 1),
                                    bullet.direction.y * -1 + random.uniform(-1, 1),
                                    random.randint(4, 16),
                                    (
                                        random.randint(90, 170),
                                        random.randint(0, 40),
                                        random.randint(0, 10),
                                    ),
                                )
                            )
                        self.enemies.remove(enemy)
                        self.destroyed_enemies += 1
                        log(
                            f"💥 Bullet hit enemy! Enemy destroyed. Total destroyed: {self.destroyed_enemies}"
                        )
                    else:
                        for _ in range(5):
                            self.particles.append(
                                Particle(
                                    bullet.rect.centerx,
                                    bullet.rect.centery,
                                    "particle",
                                    bullet.direction.x * -1 + random.uniform(-1, 1),
                                    bullet.direction.y * -1 + random.uniform(-1, 1),
                                    random.randint(4, 16),
                                    (
                                        random.randint(90, 170),
                                        random.randint(0, 40),
                                        random.randint(0, 10),
                                    ),
                                )
                            )
                        log(f"💥 Bullet hit enemy! Enemy health: {enemy.health}")
                    self.bullets.remove(bullet)
                    break
            if (
                self.player.collision_rect.colliderect(enemy.collision_rect)
                and self.immortal_time <= 0
            ):
                self.player.health -= 1
                log(f"❤️ Player hit by enemy! Health: {self.player.health}")
                self.immortal_time = IMMORTAL_TIME
                for _ in range(5):
                    self.particles.append(
                        Particle(
                            self.player.collision_rect.centerx,
                            self.player.collision_rect.centery,
                            "particle",
                            random.uniform(-2, 2),
                            random.uniform(-2, 2),
                            random.randint(4, 16),
                            (
                                random.randint(90, 170),
                                random.randint(0, 40),
                                random.randint(0, 10),
                            ),
                        )
                    )
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

        return None

    def draw(self):
        self.screen.fill(COLOR_BLACK)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        for shield in self.shields:
            shield.draw(self.screen)
        for flag in self.flags:
            flag.draw(self.screen)
        for factory in self.tank_factories:
            factory.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for missile in self.missiles:
            missile.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)
        self.player.draw(self.screen)
        health_color = (
            (0, 255, 0)
            if self.player.health > 2
            else (255, 255, 0) if self.player.health == 2 else (255, 0, 0)
        )
        health_text = self.font.render(
            f"Health: {self.player.health}", True, health_color
        )
        self.screen.blit(health_text, (10, 0))
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        timer_text = self.font.render(
            f"Time: {minutes:02d}:{seconds:02d}", True, (255, 255, 255)
        )
        self.screen.blit(timer_text, (340, 0))
        enemy_text = self.font.render(
            f"Enemies Destroyed: {self.destroyed_enemies}", True, (255, 255, 255)
        )
        self.screen.blit(enemy_text, (520, 0))
        game_level = self.get_game_level()

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
