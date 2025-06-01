import pygame
import sys
from config import WIN_WIDTH, WIN_HEIGHT, FPS, PLAYER_NAME
from scenes.menu_scene import MenuScene
from utils.logger import any_error_logger, log


def game():
    pygame.init()
    sys.excepthook = any_error_logger

    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Battle City Remake")
    clock = pygame.time.Clock()

    log(f"{PLAYER_NAME} has joined the game!")

    # Початкова сцена — меню
    curr_scene = MenuScene(screen)
    running = True

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            else:
                curr_scene.handle_event(e)

        # Оновлення сцени та перехід на іншу, якщо потрібно
        new_scene = curr_scene.update()
        if new_scene:
            curr_scene = new_scene

        curr_scene.draw()
        pygame.display.flip()
        clock.tick(FPS)

    log(f"{PLAYER_NAME} has left the game")
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    game()
