import sys

import pygame

from config import FPS, WINDOW_HEIGHT, WINDOW_WIDTH
from scenes.game_over_scene import GameOverScene
from scenes.game_win_scene import GameWinScene
from scenes.menu_scene import MenuScene
from utils.logger import any_error_logger, init_log_folder, log


def main():
    init_log_folder()
    log("🚀 Game started")
    sys.excepthook = any_error_logger
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Battle City Remake")
    clock = pygame.time.Clock()
    current_scene = MenuScene(screen)
    try:
        music = pygame.mixer.Sound("sounds/theme.mp3")
        music.play(-1)
    except pygame.error as e:
        log(f"⚠️ Failed to load menu theme: {e}")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                next_scene = current_scene.handle_event(event)
                if next_scene:
                    pygame.mixer.stop()
                    current_scene = next_scene
                    if (
                        not isinstance(current_scene, MenuScene)
                        or not isinstance(current_scene, GameOverScene)
                        or not isinstance(current_scene, GameWinScene)
                    ):
                        try:
                            pygame.mixer.music.load("sounds/mainTheme.mp3")
                            pygame.mixer.music.play(1)
                        except pygame.error as e:
                            log(f"⚠️ Failed to load main theme: {e}")

        next_scene = current_scene.update()
        if next_scene:
            pygame.mixer.stop()
            current_scene = next_scene
            if isinstance(current_scene, GameWinScene):
                try:
                    pygame.mixer.music.load("sounds/win.mp3")
                    pygame.mixer.music.play(1)
                except pygame.error as e:
                    log(f"⚠️ Failed to load menu theme: {e}")
            elif isinstance(current_scene, GameOverScene):
                try:
                    pygame.mixer.music.load("sounds/lose.mp3")
                    pygame.mixer.music.play(1)
                except pygame.error as e:
                    log(f"⚠️ Failed to load menu theme: {e}")
            elif isinstance(current_scene, MenuScene):
                try:
                    pygame.mixer.music.load("sounds/theme.mp3")
                    pygame.mixer.music.play(1)
                except pygame.error as e:
                    log(f"⚠️ Failed to load menu theme: {e}")
            else:
                try:
                    pygame.mixer.music.load("sounds/mainTheme.mp3")
                    pygame.mixer.music.play(1)
                except pygame.error as e:
                    log(f"⚠️ Failed to load main theme: {e}")

        current_scene.draw()
        pygame.display.flip()
        clock.tick(FPS)

    log("🛑 Game exited")
    pygame.mixer.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
