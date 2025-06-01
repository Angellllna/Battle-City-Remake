import pygame

from config import BLACK, WHITE, PLAYER_NAME
from utils.logger import any_error_logger, log


class MenuScene:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 36)
        self.title_text = self.font.render("Натисніть ENTER, щоб почати", True, WHITE)
        self.next_scene = None

    def handle_event(self, event):
        from scenes.game_scene import GameScene
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # Enter
                log(f"{PLAYER_NAME} started the game from menu")
                self.next_scene = GameScene(self.screen)

    def update(self):
        # Якщо вибрано нову сцену — повернути її в main.py
        if self.next_scene:
            return self.next_scene

    def draw(self):
        self.screen.fill(BLACK)
        text_rect = self.title_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(self.title_text, text_rect)
