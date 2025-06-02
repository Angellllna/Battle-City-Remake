import pygame
import sys
from config import WIN_WIDTH, WIN_HEIGHT, FPS_BARRIER, PLAYER_NAME, COLOR_WHITE
from scenes.menu_scene import MenuScene
from utils.logger import any_error_logger, log

class FpsCounter:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 20)
        self.clock = pygame.time.Clock()
        self.fps = 0

    def update(self):
        self.fps = self.clock.get_fps()
        self.clock.tick(FPS_BARRIER)

    def draw(self):
        fps_text = self.font.render(f'FPS: {self.fps:.0f}', True, COLOR_WHITE)
        self.screen.blit(fps_text, (10, 40))

def game():
    pygame.init()
    sys.excepthook = any_error_logger

    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Battle City Remake")
    fps_counter = FpsCounter(screen)
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

        fps_counter.update()
        curr_scene.draw()

        fps_counter.draw()
        pygame.display.flip()
        clock.tick(FPS_BARRIER)

    log(f"{PLAYER_NAME} has left the game")
    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    game()
