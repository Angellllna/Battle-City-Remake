import pygame
from config import OBSTACLE_SIZE, COLOR_GRAY, PLAYER_SPEED, WINDOW_WIDTH, WINDOW_HEIGHT, PLAYER_SIZE
from entities.bullet import Missile

class Enemy:
    def __init__(self, x, y, direction="horizontal"):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.color = COLOR_GRAY
        self.speed = PLAYER_SPEED - 1
        self.direction = direction

    def move(self, obstacles):
        dx = dy = 0
        if self.direction == "horizontal":
            dx = self.speed
        elif self.direction == "vertical":
            dy = self.speed

        new_rect = self.rect.move(dx, dy)
        hit_wall = (
            new_rect.left < 0 or new_rect.right > WINDOW_WIDTH or
            new_rect.top < 0 or new_rect.bottom > WINDOW_HEIGHT
        )
        hit_obstacle = False
        for obstacle in obstacles:
            if obstacle.blocks_movement:
                if new_rect.colliderect(obstacle.rect):
                    hit_obstacle = True
                    break
            if hit_obstacle:
                break

        if hit_wall or hit_obstacle:
            self.speed *= -1
        else:
            self.rect = new_rect

    def find_path(self, maze, start, end):
        rows, cols = len(maze), len(maze[0])
        queue = [start]
        visited = {start}
        parent = {start: None}
        while queue:
            x, y = queue.pop(0)
            if (x, y) == end:
                path = []
                current = (x, y)
                while current is not None:
                    path.append(current)
                    current = parent[current]
                return path[::-1]
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < rows and 0 <= ny < cols and
                    maze[nx][ny] == 0 and (nx, ny) not in visited):
                    queue.append((nx, ny))
                    visited.add((nx, ny))
                    parent[(nx, ny)] = (x, y)
        return [start]

    def move_toward_player(self, player, maze_matrix):
        tile_size = OBSTACLE_SIZE
        rows, cols = len(maze_matrix), len(maze_matrix[0])
    
        start_x = self.rect.centerx // tile_size
        start_y = self.rect.centery // tile_size
        start_x = max(0, min(start_x, cols - 1))
        start_y = max(0, min(start_y, rows - 1))
        start = (start_y, start_x)
    
        end_x = player.rect.centerx // tile_size
        end_y = player.rect.centery // tile_size
        end_x = max(0, min(end_x, cols - 1))
        end_y = max(0, min(end_y, rows - 1))
        end = (end_y, end_x)
    
        self.path = self.find_path(maze_matrix, start, end)
        if len(self.path) > 1:
            next_cell = self.path[1]
            dx = (next_cell[1] * tile_size + tile_size // 2) - self.rect.centerx
            dy = (next_cell[0] * tile_size + tile_size // 2) - self.rect.centery
            new_rect = self.rect.copy()
            if abs(dx) > abs(dy):
                new_rect.x += self.speed if dx > 0 else -self.speed
            else:
                new_rect.y += self.speed if dy > 0 else -self.speed

            for obstacle in self.obstacles:
                if obstacle.blocks_movement:
                    if new_rect.colliderect(obstacle.rect):
                        return
            self.rect = new_rect

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class ChasingEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, direction="chasing")
        self.color = (150, 50, 50)
        self.shoot_cooldown = 60
        self.cooldown_timer = 0
        self.direction = pygame.Vector2(0, -1)
        self.obstacles = []

    def update(self, player, maze_matrix, obstacles):
        self.move_toward_player(player, maze_matrix)
        
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
        
        if self.cooldown_timer == 0:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            direction = pygame.Vector2(dx, dy)
            if direction.length_squared() > 0:
                self.direction = direction.normalize()
            missile = self.shoot()
            self.cooldown_timer = self.shoot_cooldown
            return missile
        return None

    def shoot(self):
        return Missile(self.rect.centerx - 4, self.rect.centery - 4, self.direction)

    def move(self, obstacles):
        pass