import pygame
import sys
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from scenes.menu_scene import MenuScene
from utils.logger import log

def main():
    log("🚀 Game started")
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Battle City Remake")
    clock = pygame.time.Clock()

    current_scene = MenuScene(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            current_scene.handle_event(event)

        next_scene = current_scene.update()
        if next_scene:
            current_scene = next_scene

        current_scene.draw()
        pygame.display.flip()
        clock.tick(FPS)

    log("🛑 Game exited")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
