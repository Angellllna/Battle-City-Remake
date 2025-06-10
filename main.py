import pygame
from entities.player import Player
from entities.flag import Flag
from entities.defend_flag import DefendFlag
from map import create_test_map
from entities.obstacle import BushBlock, SteelBlock, Shield


pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((512, 448))
pygame.display.set_caption("Battle City Remake")
clock = pygame.time.Clock()

player = Player(position=(100, 300), speed=2)
flag = Flag(x=100, y=300)  # Прапор гравця
defend_flag = DefendFlag(x=224, y=416)  # Захисний прапор (внизу)


obstacles = create_test_map()
last_pressed_direction = pygame.Vector2(0, 0)

# Поки що ворогів нема — для тесту можемо тимчасово дати "гравця" як ворога
enemy_tanks = [player]  # Тест: гравець буде вважатися ворогом

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                last_pressed_direction = pygame.Vector2(0, -1)
            elif event.key == pygame.K_DOWN:
                last_pressed_direction = pygame.Vector2(0, 1)
            elif event.key == pygame.K_LEFT:
                last_pressed_direction = pygame.Vector2(-1, 0)
            elif event.key == pygame.K_RIGHT:
                last_pressed_direction = pygame.Vector2(1, 0)
            elif event.key == pygame.K_SPACE:
                player.shoot()

        elif event.type == pygame.KEYUP:
            key_to_dir = {
                pygame.K_UP: pygame.Vector2(0, -1),
                pygame.K_DOWN: pygame.Vector2(0, 1),
                pygame.K_LEFT: pygame.Vector2(-1, 0),
                pygame.K_RIGHT: pygame.Vector2(1, 0)
            }
            if event.key in key_to_dir and last_pressed_direction == key_to_dir[event.key]:
                last_pressed_direction = pygame.Vector2(0, 0)
                
                
    # for ob in obstacles:
    #     if isinstance(ob, BushBlock) and player.rect.colliderect(ob.rect):
    #         ob.trigger_shake()

    player.move(last_pressed_direction.x, last_pressed_direction.y, obstacles)
    player.update_bullets(screen.get_rect())

    for enemy in enemy_tanks[:]:
        for obstacle in obstacles:
            if isinstance(obstacle, Shield):
                if enemy.rect.colliderect(obstacle.rect):
                    print(f"⚡ Ворог знищений щитом!")
                    enemy_tanks.remove(enemy)
                    break

    flag.check_capture(player)
    defend_flag.check_capture(enemy_tanks)

    if defend_flag.captured:
        print("⚠️ Базу захоплено! Гру програно.")
        

    for bullet in player.bullets[:]:
        for obstacle in obstacles[:]:
            target_rects = obstacle.get_collision_rects() if hasattr(obstacle, "get_collision_rects") else [obstacle.rect]

            if any(bullet.rect.colliderect(r) for r in target_rects):
                if obstacle.blocks_bullets:
                    player.bullets.remove(bullet)
                    if hasattr(obstacle, "hit") and obstacle.hit(bullet):
                        obstacles.remove(obstacle)
                    break
    
                

    screen.fill((0, 0, 0))

    for ob in obstacles:
        if not isinstance(ob, BushBlock):
            ob.draw(screen)
            
    player.update()

    player.draw(screen)
    
    defend_flag.draw(screen)
    
    for ob in obstacles:
        if isinstance(ob, BushBlock):
            ob.draw(screen)

    flag.draw(screen)  # Захоплюваний прапор — над гравцем

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
