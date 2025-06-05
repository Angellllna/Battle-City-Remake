import pygame
import math
from config import COLOR_BLACK, COLOR_WHITE
from utils.logger import log

class MenuScene:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 36)
        self.title_text = self.font.render("Натисніть ENTER, щоб почати", True, (0, 255, 0))
        self.next_scene = None

        # Загружаемо лого
        try:
            self.logo = pygame.image.load("logo.png").convert_alpha()
            logo_width = 400
            logo_height = 200
            self.logo = pygame.transform.scale(self.logo, (logo_width, logo_height))
        except pygame.error as e:
            log(f"🔴 Не удалось загрузить логотип: {e}")
            self.logo = None

        # настройка ремейку
        self.remake_base_size = 50
        self.remake_amplitude = 5
        self.remake_speed = 3
        self.start_ticks = pygame.time.get_ticks()

        self.remake_font_name = "arial"

    def handle_event(self, event):
        from scenes.game_scene import GameScene
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                log("🟢 Player started the game from menu")
                self.next_scene = GameScene(self.screen)

    def update(self):
        if self.next_scene:
            return self.next_scene

    def draw(self):
        self.screen.fill(COLOR_BLACK)
        # хитромудра система лого і надпису ремейк
        if self.logo:
            logo_rect = self.logo.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 100))
            self.screen.blit(self.logo, logo_rect)
            time_passed = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
            scale = self.remake_base_size + self.remake_amplitude * math.sin(time_passed * self.remake_speed)
            remake_font = pygame.font.SysFont(self.remake_font_name, int(scale))
            remake_text = remake_font.render("Remake", True, (255,255,0))
            rotated_text = pygame.transform.rotate(remake_text, 45)
            offset_x = 45
            offset_y = 30
            rotated_rect = rotated_text.get_rect(center=(logo_rect.right - offset_x, logo_rect.centery + offset_y))
            self.screen.blit(rotated_text, rotated_rect)
        text_rect = self.title_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 100))
        self.screen.blit(self.title_text, text_rect)
