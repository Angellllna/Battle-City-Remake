import pygame
from config import *
from scenes.menu_scene import MenuScene
from utils.logger import log

class GameOverScene:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 36)
        self.title_text = self.font.render("Гру завершено", True, COLOR_WHITE)
        self.info_text = self.font.render("Натисніть ENTER, щоб повернутись у меню", True, COLOR_WHITE)
        self.next_scene = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                log("Повернення у меню з Game Over сцени")
                self.next_scene = MenuScene(self.screen)

    def update(self):
        if self.next_scene:
            return self.next_scene

    def draw(self):
        self.screen.fill(COLOR_BLACK)
        title_rect = self.title_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 30))
        info_rect = self.info_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 30))
        self.screen.blit(self.title_text, title_rect)
        self.screen.blit(self.info_text, info_rect)
