import os
import sys
import pygame
def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    # Обрезка
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image



clock = pygame.time.Clock()
pygame.init()
size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)
bomb1_image = load_image("g11.jpg", -1)
bomb1_image = pygame.transform.scale(bomb1_image,(200, 200))
bomb1_image1 = pygame.transform.rotate(bomb1_image, 2)
space_ship = pygame.sprite.Group()
bomb1 = pygame.sprite.Sprite(space_ship)
bomb1.image = bomb1_image
bomb1.rect = bomb1.image.get_rect()
bomb1.rect.x = 500
bomb1.rect.y = 500
r = True
o = 1
while r:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            r = False
    o += 1
    bomb1_image1 = pygame.transform.rotate(bomb1_image, o)
    space_ship.draw(screen)
    bomb1.image = bomb1_image1
    bomb1.rect = bomb1.image.get_rect()
    bomb1.rect.x = 500
    bomb1.rect.y = 500
    pygame.display.flip()

    screen.fill(pygame.Color('black'))
    clock.tick(100)