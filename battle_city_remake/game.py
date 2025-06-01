from pygame import *
import pygame
from config import *
import sys
from scenes.menu_scene import MenuScene
from utils.logger import any_error_logger, log


#me


def game():
    #initializes pygame, makes window, something basic, etc.
    pygame.init()
    sys.excepthook = any_error_logger
    screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption('Battle City Remake')
    clock = pygame.time.Clock()
    log(f"{PLAYER_NAME} has joined the game!")

    #sets the main game's window as current
    curr_scene = MenuScene(screen)
    
    running = True #<-- Makes your game booted up
    #game cycle
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                
        #render textures, scenes, sets fps, etc.
        curr_scene.update()
        curr_scene.draw()
        pygame.display.flip()
        clock.tick(FPS)

    #exit things
    log(f"{PLAYER_NAME} has left the game")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game()



