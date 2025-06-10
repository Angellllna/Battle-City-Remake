import pygame
import sys
from config import WIN_WIDTH, WIN_HEIGHT, FPS_BARRIER, PLAYER_NAME, FPS_COLOR, FPS_X, FPS_Y, SHOW_FPS
from scenes.menu_scene import MenuScene
from utils.logger import any_error_logger, log
from random import randint

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
        fps_text = self.font.render(f'FPS: {self.fps:.0f}', True, FPS_COLOR)
        self.screen.blit(fps_text, (FPS_X, FPS_Y))

def game():
    pygame.init()
    sys.excepthook = any_error_logger

    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Battle City Remake")
    clock = pygame.time.Clock()

    fps_counter = FpsCounter(screen)
    fps_log_printed = False

    rand_num = randint(0, 10000)


    log(f"\n=====================================\n{PLAYER_NAME} has joined the game!")

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

        if SHOW_FPS:
            fps_counter.draw()
            if not fps_log_printed:
                log(f'{PLAYER_NAME} has used FPS Counter :)')
                fps_log_printed = True
        
        if rand_num == 7831:
            log('he he\n dis play will posted to locial nuws!\n Cal -1782930727\n message bai ze stronest fairy')

        elif rand_num == 144:
            log('dont listen to this, this is scam, i checked. how? secret ;)')


        pygame.display.flip()
        clock.tick(FPS_BARRIER)

    log(f"{PLAYER_NAME} has left the game\n=====================================\n")
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    game()
