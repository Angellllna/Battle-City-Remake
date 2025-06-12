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
    PLAYER_SIZE
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
    Turret
)
from entities.particle import Particle
from entities.player import Player
from entities.powerups import Part
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
        self.parts = []
        self.turrets = []
        for row_index, row in enumerate(MAP1):
            for col_index, cell in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if cell == "fl":
                    self.flags.append(DefendFlag(x, y))

        for row_index, row in enumerate(MAP1):
            for col_index, cell in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
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
        try:
            self.health_icon = pygame.image.load(os.path.join("textures", "health.png")).convert_alpha()
            self.health_icon = pygame.transform.scale(self.health_icon, (OBSTACLE_SIZE, OBSTACLE_SIZE))
            self.health_icon.fill((0, 255, 0), special_flags=pygame.BLEND_RGBA_MULT)
        except:
            self.health_icon = pygame.Surface((OBSTACLE_SIZE, OBSTACLE_SIZE))
            self.health_icon.fill((0, 255, 0))
        try:
            self.damage_icon = pygame.image.load(os.path.join("textures", "damage.png")).convert_alpha()
            self.damage_icon = pygame.transform.scale(self.damage_icon, (OBSTACLE_SIZE, OBSTACLE_SIZE))
            self.damage_icon.fill((255, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        except:
            self.damage_icon = pygame.Surface((OBSTACLE_SIZE, OBSTACLE_SIZE))
            self.damage_icon.fill((255, 0, 0))
        try:
            self.speed_icon = pygame.image.load(os.path.join("textures", "speed.png")).convert_alpha()
            self.speed_icon = pygame.transform.scale(self.speed_icon, (OBSTACLE_SIZE, OBSTACLE_SIZE))
            self.speed_icon.fill((0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        except:
            self.speed_icon = pygame.Surface((OBSTACLE_SIZE, OBSTACLE_SIZE))
            self.speed_icon.fill((0, 0, 255))
        try:
            self.turret_icon = pygame.image.load(os.path.join("textures", "turret.png")).convert_alpha()
            self.turret_icon = pygame.transform.scale(self.turret_icon, (OBSTACLE_SIZE, OBSTACLE_SIZE))
            self.turret_icon.fill((255, 255, 0), special_flags=pygame.BLEND_RGBA_MULT)
        except:
            self.turret_icon = pygame.Surface((OBSTACLE_SIZE, OBSTACLE_SIZE))
            self.turret_icon.fill((255, 255, 0))
        try:
            self.enemies_destroyed_icon = pygame.image.load(os.path.join("textures", "enemies_destroyed.png")).convert_alpha()
            self.enemies_destroyed_icon = pygame.transform.scale(self.enemies_destroyed_icon, (OBSTACLE_SIZE, OBSTACLE_SIZE))
            self.enemies_destroyed_icon.fill((255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
        except:
            self.enemies_destroyed_icon = pygame.Surface((OBSTACLE_SIZE, OBSTACLE_SIZE))
            self.enemies_destroyed_icon.fill((255, 255, 255))
        try:
            self.shield_icon = pygame.image.load(os.path.join("textures", "shield1.png")).convert_alpha()
            self.shield_icon = pygame.transform.scale(self.shield_icon, (OBSTACLE_SIZE, OBSTACLE_SIZE))
            self.shield_icon.fill((0, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
        except:
            self.shield_icon = pygame.Surface((OBSTACLE_SIZE, OBSTACLE_SIZE))
            self.shield_icon.fill((0, 255, 255))
        try:
            self.time_icon = pygame.image.load(os.path.join("textures", "time.png")).convert_alpha()
            self.time_icon = pygame.transform.scale(self.time_icon, (OBSTACLE_SIZE, OBSTACLE_SIZE))
            self.time_icon.fill((255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
        except:
            self.time_icon = pygame.Surface((OBSTACLE_SIZE, OBSTACLE_SIZE))
            self.time_icon.fill((255, 255, 255))

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
                    bullet.source = self.player  # Set player as bullet source
                    self.bullets.append(bullet)
                    for _ in range(5):
                        self.particles.append(Particle(self.player.x + PLAYER_SIZE / 2, self.player.y + PLAYER_SIZE / 2, "particle", self.player.direction[0] + random.uniform(-1, 1), self.player.direction[1] + random.uniform(-1, 1), random.randint(4, 16), (80, 80, 80)))
                    if self.shoot_sound:
                        self.shoot_sound.play()
            elif event.key == pygame.K_ESCAPE:
                pygame.mixer.stop()
                log("🚪 Exit to GameOverScene on ESC")
                return GameOverScene(self.screen)
            if event.key == pygame.K_q and self.player.turrets_count > 0:
                turret = Turret(int((self.player.x + PLAYER_SIZE / 2) / 40) * 40, int((self.player.y + PLAYER_SIZE / 2) / 40) * 40)
                self.turrets.append(turret)
                self.player.turrets_count -= 1
            elif event.key == pygame.K_e and self.player.shields_count > 0:
                shield = Shield(int((self.player.x + PLAYER_SIZE / 2) / 40) * 40, int((self.player.y + PLAYER_SIZE / 2) / 40) * 40)
                self.shields.append(shield)
                self.player.shields_count -= 1

        return None

    def update_maze_matrix(self):
        tile_size = OBSTACLE_SIZE
        rows = WINDOW_HEIGHT // tile_size
        cols = WINDOW_WIDTH // tile_size
        maze_matrix = [[0 for _ in range(cols)] for _ in range(rows)]
        for obstacle in self.obstacles:
            if obstacle.blocks_movement:
                x = obstacle.rect.x // tile_size
                y = obstacle.rect.y // tile_size
                if 0 <= x < cols and 0 <= y < rows:
                    maze_matrix[y][x] = 1
        return maze_matrix

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

        for part in self.parts[:]:
            if self.player.collision_rect.colliderect(part.rect):
                self.player.collect_part(part)
                self.parts.remove(part)
                log(f"🛠️ Player collected {part.type} part")

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
                            self.obstacles.remove(obstacle)
                        self.bullets.remove(bullet)
                        log("🧱 Bullet hit obstacle")
                        break
            for turret in self.turrets[:]:
                if bullet.rect.colliderect(turret.collision_rect) and bullet.source != turret:
                    destroyed = turret.hit(bullet)
                    self.bullets.remove(bullet)
                    if destroyed:
                        for _ in range(5):
                            self.particles.append(
                                Particle(
                                    turret.rect.centerx,
                                    turret.rect.centery,
                                    "particle",
                                    random.uniform(-2, 2),
                                    random.uniform(-2, 2),
                                    random.randint(4, 16),
                                    (255, 255, 0),
                                )
                            )
                        self.turrets.remove(turret)
                        log("💥 Turret destroyed by bullet")
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
                for shield in self.shields[:]:
                    if missile.rect.colliderect(shield.rect):
                        destroyed = shield.hit(missile)
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
                        if destroyed:
                            for _ in range(5):
                                self.particles.append(
                                    Particle(
                                        shield.rect.centerx,
                                        shield.rect.centery,
                                        "particle",
                                        random.uniform(-2, 2),
                                        random.uniform(-2, 2),
                                        random.randint(4, 16),
                                        (0, 255, 255),
                                    )
                                )
                            self.shields.remove(shield)
                            log("🛡️ Shield destroyed by missile")
                        self.missiles.remove(missile)
                        break
                else:
                    for turret in self.turrets[:]:
                        if missile.rect.colliderect(turret.collision_rect):
                            destroyed = turret.hit(missile)
                            for _ in range(5):
                                self.particles.append(
                                    Particle(
                                        turret.rect.centerx,
                                        turret.rect.centery,
                                        "particle",
                                        random.uniform(-2, 2),
                                        random.uniform(-2, 2),
                                        random.randint(4, 16),
                                        (255, 255, 0),
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
                            self.missiles.remove(missile)
                            if destroyed:
                                self.turrets.remove(turret)
                                log("💥 Turret destroyed by missile")
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
        for turret in self.turrets:
            turret.update(self.enemies, self.bullets)
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
                missile = enemy.update(self.player, maze_matrix, self.obstacles, self.turrets)
                if missile:
                    self.missiles.append(missile)
                    if self.shoot_sound:
                        self.shoot_sound.play()
            elif isinstance(enemy, FlagChasingEnemy):
                maze_matrix = self.update_maze_matrix()
                enemy.update(self.player, maze_matrix, self.obstacles, self.turrets)
            else:
                enemy.move(self.obstacles)
            for shield in self.shields[:]:
                if enemy.collision_rect.colliderect(shield.rect):
                    destroyed = shield.hit()
                    if destroyed:
                        for _ in range(5):
                            self.particles.append(
                                Particle(
                                    shield.rect.centerx,
                                    shield.rect.centery,
                                    "particle",
                                    random.uniform(-2, 2),
                                    random.uniform(-2, 2),
                                    random.randint(4, 16),
                                    (0, 255, 255),
                                )
                            )
                        self.shields.remove(shield)
                        log("🛡️ Shield destroyed by enemy")
                    part = Part(enemy.x + PLAYER_SIZE / 2 - OBSTACLE_SIZE // 4, enemy.y + PLAYER_SIZE / 2 - OBSTACLE_SIZE // 4)
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
                    if part:
                        self.parts.append(part)
                        log(f"🛠️ Enemy dropped {part.type} part")
                    if enemy in self.enemies:  # Fix: Check if enemy is still in list
                        self.enemies.remove(enemy)
                        log(f"🛡️ Enemy destroyed by shield. Total destroyed: {self.destroyed_enemies}")
                    break
            for bullet in self.bullets[:]:
                if bullet.rect.colliderect(enemy.collision_rect):
                    destroyed, part = enemy.hit()
                    if destroyed:
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
                        if part:
                            self.parts.append(part)
                            log(f"🛠️ Enemy dropped {part.type} part")
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
        for part in self.parts:
            part.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for turret in self.turrets:
            turret.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for missile in self.missiles:
            missile.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)
        self.player.draw(self.screen)

        health_color = (0, 255, 0) if self.player.health > self.player.max_health * 0.5 else (255, 255, 0) if self.player.health > self.player.max_health * 0.25 else (255, 0, 0)
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60

        self.screen.blit(self.health_icon, (0, 0))
        count_text = self.font.render(f"{self.player.health}/{self.player.max_health}", True, health_color)
        self.screen.blit(count_text, (40, 5))

        self.screen.blit(self.damage_icon, (110, 0))
        count_text = self.font.render(f"{self.player.damage}", True, (255, 0, 0))
        self.screen.blit(count_text, (150, 5))

        self.screen.blit(self.speed_icon, (220, 0))
        count_text = self.font.render(f"{self.player.speed}", True, (0, 0, 255))
        self.screen.blit(count_text, (260, 5))

        # Турелі
        self.screen.blit(self.turret_icon, (360, 0))
        count_text = self.font.render(f"x{self.player.turrets_count}", True, (255, 255, 255))
        self.screen.blit(count_text, (400, 5))

        # Щити
        self.screen.blit(self.shield_icon, (470, 0))
        count_text = self.font.render(f"x{self.player.shields_count}", True, (255, 255, 255))
        self.screen.blit(count_text, (510, 5))

        self.screen.blit(self.enemies_destroyed_icon, (660, 0))
        count_text = self.font.render(f":{self.destroyed_enemies}", True, (255, 255, 255))
        self.screen.blit(count_text, (700, 5))

        self.screen.blit(self.time_icon, (760, 0))
        count_text = self.font.render(f":{minutes:02d}:{seconds:02d}", True, (255, 255, 255))
        self.screen.blit(count_text, (800, 5))
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