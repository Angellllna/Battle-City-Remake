import pygame
import heapq
import random
import math
from config import OBSTACLE_SIZE, COLOR_GRAY, PLAYER_SPEED, WINDOW_WIDTH, WINDOW_HEIGHT, PLAYER_SIZE
from entities.bullet import Missile
from entities.powerups import Part

class Enemy:
    def __init__(self, x, y, direction="horizontal", level=1):
        self.x = float(x)
        self.y = float(y)
        self.collision_rect = pygame.Rect(int(self.x), int(self.y), PLAYER_SIZE, PLAYER_SIZE)
        self.base_speed = PLAYER_SPEED - 1
        self.speed = self.base_speed * (1.0 + 0.2 * (level - 1))
        self.direction = direction
        self.level = level
        self.health = level
        self.damage = level
        self.color = (180, 180, 180)
        try:
            if self.direction == "random":
                texture_prefix = f"tank2{self.level}"
                self.images = [
                    pygame.image.load(f"textures/{texture_prefix}1.png").convert_alpha(),
                    pygame.image.load(f"textures/{texture_prefix}2.png").convert_alpha()
                ]
                self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]
                for img in self.images:
                    img.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
            else:
                self.images = [
                    pygame.image.load(f"textures/tank111.png").convert_alpha(),
                    pygame.image.load(f"textures/tank112.png").convert_alpha()
                ]
                self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]
                for img in self.images:
                    img.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
            self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]
            for img in self.images:
                img.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
            if self.direction == "random":
                self.color = (100, 180, 100)
                for img in self.images:
                    img.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
        except pygame.error as e:
            print(f"Error loading enemy tank images for level {self.level}: {e}")
            self.images = [pygame.Surface((PLAYER_SIZE, PLAYER_SIZE)) for _ in range(2)]
            for img in self.images:
                img.fill(COLOR_GRAY if self.direction != "random" else (140, 100, 255))
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.animation_timer = 0
        self.animation_delay = 200
        self.moving = False
        self.current_angle = 0
        self.target_angle = 0
        self.rotation_speed = 10
        self.vector_direction = pygame.Vector2(1 if direction == "horizontal" else 0, 1 if direction == "vertical" else 0)
        self.move_type = None
        self.move_timer = 0
        self.move_duration = 300
        self.recent_directions = []
        self.max_recent_directions = 3
        if self.direction == "random":
            self.move_type = random.randint(1, 4)

    def hit(self):
        self.health -= 1
        drop_chance = 0.4 if self.level == 1 else 0.6 if self.level == 2 else 0.7
        part = None
        if self.health <= 0 and random.random() < drop_chance:
            part = Part(self.x, self.y)
        return self.health <= 0, part

    def move(self, obstacles):
        if self.direction != "random":
            dx = dy = 0
            if self.direction == "horizontal":
                dx = self.speed
            elif self.direction == "vertical":
                dy = self.speed
            new_x = self.x + dx
            new_y = self.y + dy
            new_rect = pygame.Rect(int(new_x), int(new_y), PLAYER_SIZE, PLAYER_SIZE)
            hit_wall = (
                new_rect.left < 0 or new_rect.right > WINDOW_WIDTH or
                new_rect.top < 0 or new_rect.bottom > WINDOW_HEIGHT
            )
            hit_obstacle = False
            for obstacle in obstacles:
                if obstacle.blocks_movement and new_rect.colliderect(obstacle.rect):
                    hit_obstacle = True
                    break
            if hit_wall or hit_obstacle:
                self.speed *= -1
                dx = -dx
                dy = -dy
            else:
                self.x = new_x
                self.y = new_y
                self.collision_rect = pygame.Rect(int(self.x), int(self.y), PLAYER_SIZE, PLAYER_SIZE)
                self.moving = True
            if dx != 0 or dy != 0:
                self.vector_direction = pygame.Vector2(dx, dy).normalize()
            self.target_angle = self.get_angle_from_direction(self.vector_direction)
            self.update_animation()
        else:
            if self.move_timer <= 0:
                available_directions = [1, 2, 3, 4]
                available_directions = [d for d in available_directions if d not in self.recent_directions]
                if not available_directions:
                    self.recent_directions.clear()
                    available_directions = [1, 2, 3, 4]
                self.move_type = random.choice(available_directions)
                self.recent_directions.append(self.move_type)
                if len(self.recent_directions) > self.max_recent_directions:
                    self.recent_directions.pop(0)
                self.move_timer = self.move_duration
            dx = dy = 0
            if self.move_type == 1:
                dx = self.speed
            elif self.move_type == 2:
                dy = self.speed
            elif self.move_type == 3:
                dx = -self.speed
            elif self.move_type == 4:
                dy = -self.speed
            new_x = self.x + dx
            new_y = self.y + dy
            new_rect = pygame.Rect(int(new_x), int(new_y), PLAYER_SIZE, PLAYER_SIZE)
            hit_wall = (
                new_rect.left < 0 or new_rect.right > WINDOW_WIDTH or
                new_rect.top < 0 or new_rect.bottom > WINDOW_HEIGHT
            )
            hit_obstacle = False
            for obstacle in obstacles:
                if obstacle.blocks_movement and new_rect.colliderect(obstacle.rect):
                    hit_obstacle = True
                    break
            if hit_wall or hit_obstacle:
                new_rect_x = pygame.Rect(int(self.x + dx), int(self.y), PLAYER_SIZE, PLAYER_SIZE)
                new_rect_y = pygame.Rect(int(self.x), int(self.y + dy), PLAYER_SIZE, PLAYER_SIZE)
                can_move_x = True
                can_move_y = True
                for obstacle in obstacles:
                    if obstacle.blocks_movement:
                        if new_rect_x.colliderect(obstacle.rect):
                            can_move_x = False
                        if new_rect_y.colliderect(obstacle.rect):
                            can_move_y = False
                if can_move_x and dx != 0:
                    self.x += dx
                    self.collision_rect = pygame.Rect(int(self.x), int(self.y), PLAYER_SIZE, PLAYER_SIZE)
                    self.moving = True
                    self.vector_direction = pygame.Vector2(dx, 0).normalize()
                elif can_move_y and dy != 0:
                    self.y += dy
                    self.collision_rect = pygame.Rect(int(self.x), int(self.y), PLAYER_SIZE, PLAYER_SIZE)
                    self.moving = True
                    self.vector_direction = pygame.Vector2(0, dy).normalize()
                else:
                    self.move_timer = 0
                    self.moving = False
            else:
                self.x = new_x
                self.y = new_y
                self.collision_rect = pygame.Rect(int(self.x), int(self.y), PLAYER_SIZE, PLAYER_SIZE)
                self.moving = True
                if dx != 0 or dy != 0:
                    self.vector_direction = pygame.Vector2(dx, dy).normalize()
            self.move_timer -= 1
            self.target_angle = self.get_angle_from_direction(self.vector_direction)
            self.update_animation()

    def get_angle_from_direction(self, direction):
        angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90
        return angle % 360

    def update_animation(self):
        now = pygame.time.get_ticks()
        if self.moving and now - self.animation_timer > self.animation_delay:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.animation_timer = now
        diff = (self.target_angle - self.current_angle) % 360
        if diff > 180:
            diff -= 360
        if abs(diff) < self.rotation_speed:
            self.current_angle = self.target_angle
        else:
            self.current_angle += self.rotation_speed * (1 if diff > 0 else -1)
            self.current_angle %= 360
        self.image = pygame.transform.rotate(self.images[self.image_index], self.current_angle)

    def a_star_pathfinding(self, maze, start, end):
        rows, cols = len(maze), len(maze[0])
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, end)}
        while open_set:
            current_f, current = heapq.heappop(open_set)
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                print(f"Path found for {self.__class__.__name__}: {path[::-1]}")
                return path[::-1]
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and maze[neighbor[0]][neighbor[1]] == 0:
                    tentative_g_score = g_score[current] + 1
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, end)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        print(f"No path found for {self.__class__.__name__} from {start} to {end}")
        return [start]

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def has_line_of_sight(self, player, obstacles):
        start = pygame.Vector2(self.x + PLAYER_SIZE / 2, self.y + PLAYER_SIZE / 2)
        end = pygame.Vector2(player.x + PLAYER_SIZE / 2, player.y + PLAYER_SIZE / 2)
        steps = int(start.distance_to(end) / 5)
        if steps == 0:
            return True
        direction = (end - start).normalize()
        for i in range(steps):
            point = start + direction * (i * 5)
            for obstacle in obstacles:
                if obstacle.blocks_bullets and obstacle.rect.collidepoint(point):
                    return False
        return True

    def move_toward_target(self, target_rect, maze_matrix, obstacles, range_to):
        tile_size = OBSTACLE_SIZE
        rows, cols = len(maze_matrix), len(maze_matrix[0])
        start_x = int(self.x + PLAYER_SIZE / 2) // tile_size
        start_y = int(self.y + PLAYER_SIZE / 2) // tile_size
        start_x = max(0, min(start_x, cols - 1))
        start_y = max(0, min(start_y, rows - 1))
        start = (start_y, start_x)
        end_x = target_rect.centerx // tile_size
        end_y = target_rect.centery // tile_size
        end_x = max(0, min(end_x, cols - 1))
        end_y = max(0, min(end_y, rows - 1))
        end = (end_y, end_x)
        self.path = self.a_star_pathfinding(maze_matrix, start, end)
        if len(self.path) > range_to:
            next_cell = self.path[range_to]
            dx = (next_cell[1] * tile_size + tile_size // 2) - (self.x + PLAYER_SIZE / 2)
            dy = (next_cell[0] * tile_size + tile_size // 2) - (self.y + PLAYER_SIZE / 2)
            new_x = self.x
            new_y = self.y
            if abs(dx) > abs(dy):
                new_x += self.speed if dx > 0 else -self.speed
            else:
                new_y += self.speed if dy > 0 else -self.speed
            new_rect = pygame.Rect(int(new_x), int(new_y), PLAYER_SIZE, PLAYER_SIZE)
            collision = False
            for obstacle in obstacles:
                if obstacle.blocks_movement and new_rect.colliderect(obstacle.rect):
                    collision = True
                    break
            if not collision:
                self.x = new_x
                self.y = new_y
                self.collision_rect = pygame.Rect(int(self.x), int(self.y), PLAYER_SIZE, PLAYER_SIZE)
                self.moving = True
                self.vector_direction = pygame.Vector2(dx, dy).normalize() if dx != 0 or dy != 0 else self.vector_direction
            else:
                new_rect_x = pygame.Rect(int(self.x + (self.speed if dx > 0 else -self.speed)), int(self.y), PLAYER_SIZE, PLAYER_SIZE)
                new_rect_y = pygame.Rect(int(self.x), int(self.y + (self.speed if dy > 0 else -self.speed)), PLAYER_SIZE, PLAYER_SIZE)
                can_move_x = True
                can_move_y = True
                for obstacle in obstacles:
                    if obstacle.blocks_movement:
                        if new_rect_x.colliderect(obstacle.rect):
                            can_move_x = False
                        if new_rect_y.colliderect(obstacle.rect):
                            can_move_y = False
                if can_move_x:
                    self.x += self.speed if dx > 0 else -self.speed
                    self.collision_rect = pygame.Rect(int(self.x), int(self.y), PLAYER_SIZE, PLAYER_SIZE)
                    self.moving = True
                    self.vector_direction = pygame.Vector2(self.speed if dx > 0 else -self.speed, 0).normalize()
                elif can_move_y:
                    self.y += self.speed if dy > 0 else -self.speed
                    self.collision_rect = pygame.Rect(int(self.x), int(self.y), PLAYER_SIZE, PLAYER_SIZE)
                    self.moving = True
                    self.vector_direction = pygame.Vector2(0, self.speed if dy > 0 else -self.speed).normalize()
                else:
                    self.moving = False
            self.target_angle = self.get_angle_from_direction(self.vector_direction)
        self.update_animation()

    def shoot(self):
        return Missile(self.x + PLAYER_SIZE / 2 - 4, self.y + PLAYER_SIZE / 2 - 4, self.vector_direction, damage=self.damage)

    def draw(self, surface):
        img_rect = self.image.get_rect(center=(int(self.x + PLAYER_SIZE / 2), int(self.y + PLAYER_SIZE / 2)))
        surface.blit(self.image, img_rect.topleft)

class ChasingEnemy(Enemy):
    def __init__(self, x, y, level=1):
        super().__init__(x, y, direction="chasing", level=level)
        self.health = self.level
        self.damage = level
        self.color = (150, 50, 50)
        try:
            texture_prefix = f"tank3{self.level}"
            self.images = [
                pygame.image.load(f"textures/{texture_prefix}1.png").convert_alpha(),
                pygame.image.load(f"textures/{texture_prefix}2.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]
            for img in self.images:
                img.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
        except pygame.error as e:
            print(f"Error loading chasing enemy tank images for level {self.level}: {e}")
            self.images = [pygame.Surface((PLAYER_SIZE, PLAYER_SIZE)) for _ in range(2)]
            for img in self.images:
                img.fill(self.color)
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.base_shoot_cooldown = 60
        self.shoot_cooldown = self.base_shoot_cooldown * (1.0 - 0.1 * (level - 1))
        self.cooldown_timer = 0
        self.vector_direction = pygame.Vector2(0, -1)
        self.obstacles = []

    def update(self, player, maze_matrix, obstacles):
        self.obstacles = obstacles
        self.move_toward_target(player.collision_rect, maze_matrix, obstacles, 1)
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
        if self.cooldown_timer == 0 and self.has_line_of_sight(player, obstacles):
            dx = (player.x + PLAYER_SIZE / 2) - (self.x + PLAYER_SIZE / 2)
            dy = (player.y + PLAYER_SIZE / 2) - (self.y + PLAYER_SIZE / 2)
            direction = pygame.Vector2(dx, dy)
            if direction.length_squared() > 0:
                self.vector_direction = direction.normalize()
                self.target_angle = self.get_angle_from_direction(self.vector_direction)
                missile = self.shoot()
                self.cooldown_timer = self.shoot_cooldown
                return missile
        return None

class RandomShootingEnemy(Enemy):
    def __init__(self, x, y, level=1):
        super().__init__(x, y, direction="random", level=level)
        self.damage = self.level - 1
        self.health = self.level * 2
        self.color = (100, 150, 100)
        try:
            texture_prefix = f"tank2{self.level}"
            self.images = [
                pygame.image.load(f"textures/{texture_prefix}1.png").convert_alpha(),
                pygame.image.load(f"textures/{texture_prefix}2.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]
            for img in self.images:
                img.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
        except pygame.error as e:
            print(f"Error loading random shooting enemy tank images for level {self.level}: {e}")
            self.images = [pygame.Surface((PLAYER_SIZE, PLAYER_SIZE)) for _ in range(2)]
            for img in self.images:
                img.fill(self.color)
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.base_shoot_cooldown = 90
        self.shoot_cooldown = self.base_shoot_cooldown * (1.0 - 0.1 * (level - 1))
        self.cooldown_timer = 0
        self.vector_direction = pygame.Vector2(0, -1)
        self.obstacles = []

    def update(self, player, maze_matrix, obstacles):
        self.obstacles = obstacles
        self.move(obstacles)
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
        if self.cooldown_timer == 0 and self.has_line_of_sight(player, obstacles):
            dx = (player.x + PLAYER_SIZE / 2) - (self.x + PLAYER_SIZE / 2)
            dy = (player.y + PLAYER_SIZE / 2) - (self.y + PLAYER_SIZE / 2)
            direction = pygame.Vector2(dx, dy)
            if direction.length_squared() > 0:
                self.vector_direction = direction.normalize()
                self.target_angle = self.get_angle_from_direction(self.vector_direction)
                missile = self.shoot()
                self.cooldown_timer = self.shoot_cooldown
                return missile
        return None

class ShootingEnemy(Enemy):
    def __init__(self, x, y, direction="horizontal", level=1):
        super().__init__(x, y, direction=direction, level=level)
        self.color = (200, 100, 50)
        try:
            texture_prefix = f"tank5{self.level}"
            self.images = [
                pygame.image.load(f"textures/tank111.png").convert_alpha(),
                pygame.image.load(f"textures/tank112.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]
            for img in self.images:
                img.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
        except pygame.error as e:
            print(f"Error loading shooting enemy tank images for level {self.level}: {e}")
            self.images = [pygame.Surface((PLAYER_SIZE, PLAYER_SIZE)) for _ in range(2)]
            for img in self.images:
                img.fill(self.color)
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.base_shoot_cooldown = 120
        self.shoot_cooldown = self.base_shoot_cooldown * (1.0 - 0.1 * (level - 1))
        self.cooldown_timer = 0
        self.vector_direction = pygame.Vector2(1 if direction == "horizontal" else 0, 1 if direction == "vertical" else 0)
        self.obstacles = []

    def update(self, player, maze_matrix, obstacles):
        self.obstacles = obstacles
        self.move(obstacles)
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
        if self.cooldown_timer == 0 and self.has_line_of_sight(player, obstacles):
            dx = (player.x + PLAYER_SIZE / 2) - (self.x + PLAYER_SIZE / 2)
            dy = (player.y + PLAYER_SIZE / 2) - (self.y + PLAYER_SIZE / 2)
            direction = pygame.Vector2(dx, dy)
            if direction.length_squared() > 0:
                self.vector_direction = direction.normalize()
                self.target_angle = self.get_angle_from_direction(self.vector_direction)
                missile = self.shoot()
                self.cooldown_timer = self.shoot_cooldown
                return missile
        return None

class BaseChasingShootingEnemy(Enemy):
    def __init__(self, x, y, flags, level=1, can_shoot=True):
        super().__init__(x, y, direction="base_chasing", level=level)
        self.flags = flags
        self.target_flag = None
        self.can_shoot = can_shoot
        self.health = self.level - 1
        self.damage = 1
        self.speed = self.speed + self.level - 1
        self.choose_target_flag()
        self.color = (50, 100, 200)
        try:
            texture_prefix = f"tank1{self.level}"
            self.images = [
                pygame.image.load(f"textures/{texture_prefix}1.png").convert_alpha(),
                pygame.image.load(f"textures/{texture_prefix}2.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]
            for img in self.images:
                img.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
        except pygame.error as e:
            print(f"Error loading base chasing enemy tank images for level {self.level}: {e}")
            self.images = [pygame.Surface((PLAYER_SIZE, PLAYER_SIZE)) for _ in range(2)]
            for img in self.images:
                img.fill(self.color)
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.base_shoot_cooldown = 60
        self.shoot_cooldown = self.base_shoot_cooldown * (1.0 - 0.1 * (level - 1))
        self.cooldown_timer = 0
        self.vector_direction = pygame.Vector2(0, -1)
        self.obstacles = []

    def choose_target_flag(self):
        if not self.flags:
            self.target_flag = None
            return
        min_distance = float('inf')
        for flag in self.flags:
            if not flag.captured:
                distance = math.sqrt(
                    (self.x + PLAYER_SIZE / 2 - flag.rect.centerx) ** 2 +
                    (self.y + PLAYER_SIZE / 2 - flag.rect.centery) ** 2
                )
                if distance < min_distance:
                    min_distance = distance
                    self.target_flag = flag

    def update(self, player, maze_matrix, obstacles):
        self.obstacles = obstacles
        if self.target_flag and not self.target_flag.captured:
            self.move_toward_target(self.target_flag.rect, maze_matrix, obstacles, 0)
        else:
            self.choose_target_flag()
            if self.target_flag:
                self.move_toward_target(self.target_flag.rect, maze_matrix, obstacles, 0)
            else:
                self.move_toward_target(player.collision_rect, maze_matrix, obstacles, 1)
        if self.can_shoot:
            if self.cooldown_timer > 0:
                self.cooldown_timer -= 1
            if self.cooldown_timer == 0 and self.has_line_of_sight(player, obstacles):
                dx = (player.x + PLAYER_SIZE / 2) - (self.x + PLAYER_SIZE / 2)
                dy = (player.y + PLAYER_SIZE / 2) - (self.y + PLAYER_SIZE / 2)
                direction = pygame.Vector2(dx, dy)
                if direction.length_squared() > 0:
                    self.vector_direction = direction.normalize()
                    self.target_angle = self.get_angle_from_direction(self.vector_direction)
                    missile = self.shoot()
                    self.cooldown_timer = self.shoot_cooldown
                    return missile
        return None

class FlagChasingEnemy(Enemy):
    def __init__(self, x, y, flags, level=1):
        super().__init__(x, y, direction="flag_chasing", level=level)
        self.flags = flags
        self.target_flag = None
        self.health = 1
        self.damage = 1
        self.speed = self.speed + self.level - 1
        self.choose_target_flag()
        self.color = (180, 180, 180)
        try:
            texture_prefix = f"tank1{self.level}"
            self.images = [
                pygame.image.load(f"textures/{texture_prefix}1.png").convert_alpha(),
                pygame.image.load(f"textures/{texture_prefix}2.png").convert_alpha()
            ]
            self.images = [pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)) for img in self.images]
            for img in self.images:
                img.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)
        except pygame.error as e:
            print(f"Error loading flag chasing enemy tank images for level {self.level}: {e}")
            self.images = [pygame.Surface((PLAYER_SIZE, PLAYER_SIZE)) for _ in range(2)]
            for img in self.images:
                img.fill(self.color)
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.vector_direction = pygame.Vector2(0, -1)
        self.obstacles = []

    def choose_target_flag(self):
        if not self.flags:
            self.target_flag = None
            return
        min_distance = float('inf')
        for flag in self.flags:
            if not flag.captured:
                distance = math.sqrt(
                    (self.x + PLAYER_SIZE / 2 - flag.rect.centerx) ** 2 +
                    (self.y + PLAYER_SIZE / 2 - flag.rect.centery) ** 2
                )
                if distance < min_distance:
                    min_distance = distance
                    self.target_flag = flag

    def update(self, player, maze_matrix, obstacles):
        self.obstacles = obstacles
        if self.target_flag and not self.target_flag.captured:
            self.move_toward_target(self.target_flag.rect, maze_matrix, obstacles, 0)
        else:
            self.choose_target_flag()
            if self.target_flag:
                self.move_toward_target(self.target_flag.rect, maze_matrix, obstacles, 0)
            else:
                self.move_toward_target(player.collision_rect, maze_matrix, obstacles, 1)
        return None