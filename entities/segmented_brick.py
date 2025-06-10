import pygame

class SegmentedBrick:
    SEGMENT_SIZE = 13  # 26 / 2

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.image = pygame.image.load("assets/brick.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (26, 26))

        # Стан сегментів: True = цілий
        self.segments = {
            'tl': True, 'tr': True,
            'bl': True, 'br': True
        }

        # Прямокутники сегментів
        self.segment_rects = {
            'tl': pygame.Rect(x, y, 13, 13),
            'tr': pygame.Rect(x + 13, y, 13, 13),
            'bl': pygame.Rect(x, y + 13, 13, 13),
            'br': pygame.Rect(x + 13, y + 13, 13, 13)
        }

    def draw(self, surface):
        for key, alive in self.segments.items():
            if alive:
                seg_rect = self.segment_rects[key]
                if key == 'tl':
                    area = pygame.Rect(0, 0, 13, 13)
                elif key == 'tr':
                    area = pygame.Rect(13, 0, 13, 13)
                elif key == 'bl':
                    area = pygame.Rect(0, 13, 13, 13)
                elif key == 'br':
                    area = pygame.Rect(13, 13, 13, 13)
                surface.blit(self.image, seg_rect.topleft, area)

    def hit(self, bullet):
        for key, seg_rect in self.segment_rects.items():
            if self.segments[key] and bullet.rect.colliderect(seg_rect):
                self.segments[key] = False
                break
        return not any(self.segments.values())  # Якщо всі False — повністю зруйновано

    @property
    def blocks_bullets(self):
        # Хоча б один сегмент блокує кулі
        return any(self.segments.values())

    @property
    def blocks_movement(self):
        # Хоча б один сегмент блокує рух
        return any(self.segments.values())

    def get_collision_rects(self):
        # Повертає лише живі сегменти
        return [r for k, r in self.segment_rects.items() if self.segments[k]]
