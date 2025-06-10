import pygame
import sys
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from scenes.menu_scene import MenuScene
from utils.logger import log

def main():
    log("🚀 Game started")
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Battle City Remake")
    clock = pygame.time.Clock()
    current_scene = MenuScene(screen)
    try:
        music = pygame.mixer.Sound("Battle-City-Remake/sounds/theme.mp3")
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
                    if not isinstance(current_scene, MenuScene):
                        try:
                            pygame.mixer.music.load("Battle-City-Remake/sounds/mainTheme.mp3")
                            pygame.mixer.music.play(-1)
                        except pygame.error as e:
                            log(f"⚠️ Failed to load main theme: {e}")
  
        next_scene = current_scene.update()
        if next_scene:
            pygame.mixer.stop()
            current_scene = next_scene
            if isinstance(current_scene, MenuScene):
                try:
                    music = pygame.mixer.Sound("Battle-City-Remake/sounds/theme.mp3")
                    music.play(-1)
                except pygame.error as e:
                    log(f"⚠️ Failed to load menu theme: {e}")
            else:
                try:
                    pygame.mixer.music.load("Battle-City-Remake/sounds/mainTheme.mp3")
                    pygame.mixer.music.play(-1)
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