import pygame
from entities.player import Player
from map import create_test_map
from entities.obstacle import BushBlock

pygame.init()
screen = pygame.display.set_mode((512, 448))
pygame.display.set_caption("Battle City Remake")
clock = pygame.time.Clock()

player = Player(position=(100, 100), speed=2)
obstacles = create_test_map()
last_pressed_direction = pygame.Vector2(0, 0)

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

    player.move(last_pressed_direction.x, last_pressed_direction.y, obstacles)
    player.update_bullets(screen.get_rect())

    # Перевірка зіткнень куль
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

    # Малюємо всі об'єкти крім кущів
    for ob in obstacles:
        if not isinstance(ob, BushBlock):
            ob.draw(screen)

    player.update()
    player.draw(screen)

    # Кущі поверх гравця
    for ob in obstacles:
        if isinstance(ob, BushBlock):
            ob.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
