import pygame
import math
from config import COLOR_BLACK, COLOR_WHITE, OBSTACLE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT, MAP2
from utils.logger import log
from entities.menu_tanks import Tank
from entities.obstacle import Obstacle, SteelBlock, WaterBlock, BushBlock

class MenuScene:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 36)
        self.title_text = self.font.render("Натисніть ENTER, щоб почати", True, (0, 255, 0))
        self.next_scene = None
        self.tank1 = Tank(0, 560, (255, 0, 0))  # Червоний
        self.tank2 = Tank(760, 0, (0, 0, 255))  # Синій
        if self.tank1.x < self.tank2.x:
            self.tank1.direction = "right"
            self.tank2.direction = "left"

        # Завантаження лого
        try:
            self.logo = pygame.image.load("textures/logo.png").convert_alpha()
            logo_width = 400
            logo_height = 200
            self.logo = pygame.transform.scale(self.logo, (logo_width, logo_height))
        except pygame.error as e:
            log(f"🔴 Не вдалося завантажити логотип: {e}")
            self.logo = None

        # Налаштування напису Remake
        self.remake_base_size = 50
        self.remake_amplitude = 5
        self.remake_speed = 3
        self.start_ticks = pygame.time.get_ticks()
        self.remake_font_name = "arial"

        # Ініціалізація локації
        self.obstacles = []
        self.init_location()

    def init_location(self):
        tile_size = OBSTACLE_SIZE
        map_menu = MAP2
        for row_index, row in enumerate(map_menu):
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

    def handle_event(self, event):
        from scenes.game_scene import GameScene
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                log("🟢 Player started the game from menu")
                self.next_scene = GameScene(self.screen)
        return self.next_scene

    def update(self):
        if self.next_scene:
            return self.next_scene
        # Оновлення танків і обробка зіткнень
        bullets_to_remove1, obstacles_to_destroy1 = self.tank1.update(self.tank2, self.obstacles)
        bullets_to_remove2, obstacles_to_destroy2 = self.tank2.update(self.tank1, self.obstacles)

        # Видалення зруйнованих перешкод
        for obstacle in set(obstacles_to_destroy1 + obstacles_to_destroy2):
            if obstacle in self.obstacles:
                self.obstacles.remove(obstacle)
                log("🧱 Obstacle destroyed")

        return None

    def draw(self):
        self.screen.fill(COLOR_BLACK)
        # Малюємо перешкоди
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        self.tank1.draw(self.screen)
        self.tank2.draw(self.screen)
        if self.logo:
            logo_rect = self.logo.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 100))
            self.screen.blit(self.logo, logo_rect)
            time_passed = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            scale = self.remake_base_size + self.remake_amplitude * math.sin(self.remake_speed * time_passed)
            remake_font = pygame.font.SysFont(self.remake_font_name, int(scale))
            remake_text = remake_font.render("Remake", True, (255, 255, 0))
            rotated_text = pygame.transform.rotate(remake_text, 45)
            offset_x = 45
            offset_y = 30
            rotated_rect = rotated_text.get_rect(center=(logo_rect.right - offset_x, logo_rect.centery + offset_y))
            self.screen.blit(rotated_text, rotated_rect)
        text_rect = self.title_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 100))
        self.screen.blit(self.title_text, text_rect)