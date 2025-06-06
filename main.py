# DEFAULT FILE ⚠️

import pygame
import sys
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from scenes.menu_scene import MenuScene

def main():
    # 1. Ініціалізація
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Battle City Remake")
    clock = pygame.time.Clock()

    # 2. Початкова сцена — меню
    current_scene = MenuScene(screen)

    # 3. Основний цикл гри
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            current_scene.handle_event(event)

        current_scene.update()
        current_scene.draw()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()