from entities.obstacle import SteelBlock, WaterBlock, BushBlock
from entities.segmented_brick import SegmentedBrick  # Новий клас

def create_test_map():
    obstacles = []

    # Рамка
    for x in range(0, 640, 16):
        obstacles.append(SteelBlock(x, 0))
        obstacles.append(SteelBlock(x, 480 - 16))
    for y in range(0, 480, 16):
        obstacles.append(SteelBlock(0, y))
        obstacles.append(SteelBlock(640 - 16, y))

    # Brick wall — тепер сегментована
    for x in range(200, 280, 26):
        obstacles.append(SegmentedBrick(x, 100))

    # Сталь
    obstacles.append(SteelBlock(300, 300))

    # Вода
    for x in range(100, 132, 16):
        obstacles.append(WaterBlock(x, 250))

    # Кущі
    for x in range(150, 182, 16):
        obstacles.append(BushBlock(x, 250))

    return obstacles
