import pygame
from config import OBSTACLE_SIZE, COLOR_GRAY, PLAYER_SPEED, WINDOW_WIDTH, WINDOW_HEIGHT, MAP1

class Enemy:
    def __init__(self, x, y, direction="horizontal"):
        self.rect = pygame.Rect(x, y, OBSTACLE_SIZE, OBSTACLE_SIZE)
        self.color = COLOR_GRAY
        self.speed = PLAYER_SPEED - 1
        self.direction = direction

    def move(self, obstacles, player):
        if self.direction != "chase":
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
            hit_obstacle = any(new_rect.colliderect(o.rect) for o in obstacles)

            if hit_wall or hit_obstacle:
                self.speed *= -1
            else:
                self.rect = new_rect
        else:
            tile_size = OBSTACLE_SIZE
            start = (self.rect.centery // tile_size, self.rect.centerx // tile_size)
            end = (player.rect.centery // tile_size, player.rect.centerx // tile_size)
            self.path = self.find_path(MAP1, start, end)
            if len(self.path) > 1:
                next_cell = self.path[1]
                dx = (next_cell[1] * tile_size + tile_size // 2) - self.rect.centerx
                dy = (next_cell[0] * tile_size + tile_size // 2) - self.rect.centery
                if abs(dx) > abs(dy):
                    self.rect.x += self.speed if dx > 0 else -self.speed
                else:
                    self.rect.y += self.speed if dy > 0 else -self.speed

    def find_path(maze, start, end):
        rows, cols = len(maze), len(maze[0])
        q = [start]  # Use list as queue
        visited = {start}
        parent = {start: None}
        while q:
            x, y = q.pop(0)  # Pop from front (BFS)
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
                        maze[nx][ny] not in ['wl'] and (nx, ny) not in visited):
                    q.append((nx, ny))
                    visited.add((nx, ny))
                    parent[(nx, ny)] = (x, y)
        return [start]


    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
