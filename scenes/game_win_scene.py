import pygame

from config import COLOR_BLACK, COLOR_WHITE
from scenes.menu_scene import MenuScene
from utils.logger import log


class GameWinScene:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 36)
        self.text = self.font.render(
            "You Win! Press ENTER to return to menu", True, COLOR_WHITE
        )
        self.next_scene = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                log("🟢 Returning to menu from GameWinScene")
                pygame.mixer.stop()
                self.next_scene = MenuScene(self.screen)

    def update(self):
        if self.next_scene:
            return self.next_scene
        return None

    def draw(self):
        self.screen.fill(COLOR_BLACK)
        text_rect = self.text.get_rect(
            center=(self.screen.get_width() // 2, self.screen.get_height() // 2)
        )
        self.screen.blit(self.text, text_rect)
