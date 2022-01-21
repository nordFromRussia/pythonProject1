import os
import sys
import pygame
from math import sqrt
import pygame_menu

pygame.init()
size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
aster_gold = pygame.sprite.Group()

pygame.mixer.music.load('mu.mp3')
pygame.mixer.music.play(-1, 0.0, 0)

# Загрузка изображения


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


def leveling(live, nam):
    # Создание карабля
    space_ship = pygame.sprite.Group()
    bomb1_image = load_image("ufo_model.png", -1)
    bomb1_image = pygame.transform.scale(bomb1_image, (70, 35))

    bomb1 = pygame.sprite.Sprite(space_ship)
    all_sprites = pygame.sprite.Group()

    bomb1.image = bomb1_image
    bomb1.rect = bomb1.image.get_rect()
    bomb1.rect.x = 0
    bomb1.rect.y = 420

    space_ship1 = pygame.sprite.Group()
    bomb1_image = load_image("Без имени-2.png")

    bombs1 = pygame.sprite.Sprite(space_ship1)

    bombs1.image = bomb1_image
    bombs1.rect = bomb1.image.get_rect()
    bombs1.rect.x = 0
    bombs1.rect.y = 0

    space_ship = pygame.sprite.Group()

    # Все состояния карабля

    bomb_image = load_image("ufo_model.png", -1)
    bomb_image = pygame.transform.scale(bomb_image, (70, 50))

    bomb_image1 = load_image("ufo_model1.png", -1)
    bomb_image1 = pygame.transform.scale(bomb_image1, (70, 50))

    # карабль летит вверх

    bomb_up = load_image("ufo_model_U.png", -1)
    bomb_up = pygame.transform.scale(bomb_up, (70, 50))

    # карабль летит вниз

    bomb_down = load_image("ufo_model_D.png", -1)
    bomb_down = pygame.transform.scale(bomb_down, (70, 50))

    bomb = pygame.sprite.Sprite(space_ship)

    bomb.image = bomb_image
    bomb.rect = bomb.image.get_rect()
    bomb.rect.x = 0
    bomb.rect.y = 400

    # Передвижение карабля

    def streak(moving_y, moving_x):
        new_x = bomb.rect.x + moving_x
        new_y = bomb.rect.y + moving_y
        if new_x < 0 or new_y < 0 or new_x > width or new_y > height:
            return None
        if new_x + 70 < 0 or new_y + 70 < 0 or new_x + 70 > width or new_y + 70 > height:
            return None
        bomb.rect.x = new_x
        bomb.rect.y = new_y

    # Передвижение хитбокса карабля

    def streak1(moving_y, moving_x):
        new_x = bomb1.rect.x + moving_x
        new_y = bomb1.rect.y + moving_y
        if new_x < 0 or new_y < 0 or new_x > width or new_y > height:
            return None
        if new_x + 70 < 0 or new_y + 70 < 0 or new_x + 70 > width or new_y + 70 > height:
            return None
        bomb1.rect.x = new_x
        bomb1.rect.y = new_y

    fon_asteroid = pygame.sprite.Group()
    winner = pygame.sprite.Group()

    # Игровое поле
    lack = open('LEVEL.txt', encoding="utf8")
    lines = lack.readlines()
    bo = []
    if len(lines) != 0:
        for i in lines:
            bo.append(i)

    # Класс остероидов
    class Asteroid:
        fon_asteroid = pygame.sprite.Group()

        def __init__(self, width1, height1, bo1, group):
            self.width = width1
            self.height = height1
            self.board = bo1

            self.board = (''.join(bo)).split('\n')
            print(self.board)
            # значения по умолчанию
            self.left = 100
            self.top = 100
            self.cell_size = 100
            for z in range(len(self.board)):
                for j in range(10):
                    if self.board[z][j] == 'Q':
                        # Сам астероид
                        meteor = load_image("asteroid.png", -1)
                        meteor = pygame.transform.scale(meteor, (100, 100))

                        meteor1 = pygame.sprite.Sprite(fon_asteroid)
                        meteor1.image = meteor
                        meteor1.rect = meteor1.image.get_rect()

                        meteor1.rect.x = z * 100
                        meteor1.rect.y = j * 100

                        meteor12 = pygame.sprite.Sprite(group)
                        meteor = pygame.transform.scale(meteor, (60, 60))
                        meteor12.image = meteor
                        meteor12.rect = meteor12.image.get_rect()

                        meteor12.rect.x = z * 100 + 20
                        meteor12.rect.y = j * 100 + 20
                    if self.board[z][j] == 'D':
                        # Золотой астероид
                        meteor = load_image("gold.png", -1)
                        meteor = pygame.transform.scale(meteor, (100, 100))

                        meteor1 = pygame.sprite.Sprite(aster_gold)
                        meteor1.image = meteor
                        meteor1.rect = meteor1.image.get_rect()

                        meteor1.rect.x = z * 100
                        meteor1.rect.y = j * 100
                    if self.board[z][j] == 'W':
                        # спрайт выйгрыша
                        meteor = load_image("win.png")
                        meteor = pygame.transform.scale(meteor, (100, 100))

                        meteor1 = pygame.sprite.Sprite(winner)
                        meteor1.image = meteor
                        meteor1.rect = meteor1.image.get_rect()

                        meteor1.rect.x = z * 100
                        meteor1.rect.y = j * 100

        # настройка внешнего вида
        def set_view(self, left1, top, cell_size):
            self.left = left1
            self.top = top
            self.cell_size = cell_size

        def render(self, screen1):
            pass

    # анимация
    class AnimatedSprite(pygame.sprite.Sprite):
        def __init__(self, sheet, columns, rows, x_cord1, y_cord1):
            super().__init__(all_sprites)
            sheet = pygame.transform.scale(sheet, (500, 375))
            self.frames = []
            self.cut_sheet(sheet, columns, rows)
            self.cur_frame = 0
            self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(x_cord1, y_cord1)

        def cut_sheet(self, sheet, columns, rows):
            self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                    sheet.get_height() // rows)
            for j in range(rows):
                for v in range(columns):
                    frame_location = (self.rect.w * v, self.rect.h * j)
                    self.frames.append(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)))

        def update(self):
            self.cur_frame = (self.cur_frame + 1) % 48
            self.image = self.frames[self.cur_frame]

    # Класс пуль
    class Bullet(pygame.sprite.Sprite):
        image = load_image("g11.jpg", 1)

        image = pygame.transform.scale(image, (10, 10))

        def __init__(self, x_cord, y_cord, group, xy):
            # НЕОБХОДИМО вызвать конструктор родительского класса Sprite. Это очень важно!!!
            super().__init__(group)
            self.image = Bullet.image
            self.rect = self.image.get_rect()

            # начальные кординаты пули
            self.rect.x = x_cord + 35
            self.rect.y = y_cord + 35

            # её скорость
            self.speed = 30.0

            # кординаты мыши
            nx, ny = xy[0], xy[1]
            print(ny)

            # синус и косинус
            sin = (-x_cord + nx) / sqrt((x_cord - nx) ** 2 + (y_cord - ny) ** 2)
            cos = (-y_cord + ny) / sqrt((x_cord - nx) ** 2 + (y_cord - ny) ** 2)

            # перемешение по икс и игрик
            self.nx, self.ny = round(sin * 10.0), round(cos * 10.0)
            self.pr = 0

        def update(self):
            self.rect.x = self.rect.x + self.nx
            self.rect.y = self.rect.y + self.ny

            self.pr += self.speed

            if self.rect.x < 0 or self.rect.y < 0 or\
                    self.rect.x > width or self.rect.y > height:
                return -1

    # переменные для проверки полёта вниз и вверх
    vv = False
    vn = False

    x, y = 0, 0

    # переменные для полёта стрельбы
    pr = False
    lev = False
    job = True
    clip = False

    # 1,5 секунд неуязвимости
    ne_damage = False

    bul = pygame.sprite.Group()
    time_damage = 0

    aster = pygame.sprite.Group()

    shoot = 0
    Asteroid(100, 100, bo, aster)
    ter = True
    killed = 0

    pausing = False

    while job:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                job = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    vv = True

                if event.key == pygame.K_DOWN:
                    vn = True

                if event.key == pygame.K_LEFT:
                    pr = True

                if event.key == pygame.K_RIGHT:
                    lev = True

                if event.key == pygame.K_ESCAPE:
                    pausing = not pausing

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    vv = False

                if event.key == pygame.K_DOWN:
                    vn = False

                if event.key == pygame.K_LEFT:
                    pr = False

                if event.key == pygame.K_RIGHT:
                    lev = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                clip = True
                Bullet(bomb.rect.x, bomb.rect.y, bul, event.pos)

            if event.type == pygame.MOUSEBUTTONUP:
                clip = False

            if event.type == pygame.MOUSEMOTION:
                x, y = event.pos

        if not pausing:
            # проверка пуль
            for i in bul:
                if i.update() == -1 or pygame.sprite.spritecollideany(i, aster, collided=None):
                    bul.remove(i)
            if bomb.image == bomb_image:
                bomb.image = bomb_image1
            else:
                bomb.image = bomb_image

            # перемещение астероидов
            for g in aster:
                g.rect.x -= 2
                g.rect.y -= 0

            for g in fon_asteroid:
                g.rect.x -= 2
                g.rect.y -= 0

            for i in aster_gold:
                if not i or pygame.sprite.spritecollideany(i, bul, collided=None):
                    aster_gold.remove(i)
                    killed += 1

            # стельба по зажиму
            if not clip:
                shoot = 0

            if clip:
                shoot += 1
                if shoot % 10 == 0:
                    Bullet(bomb.rect.x, bomb.rect.y, bul, [x, y])

            # поиск вектора перемещения
            if vv:
                up = -3
                down = 0
                bomb.image = bomb_up
            elif vn:
                down = 3
                up = 0
                bomb.image = bomb_down
            else:
                down = 0
                up = 0

            if pr:
                right = -3
                left = 0
            elif lev:
                left = 3
                right = 0
            else:
                left = 0
                right = 0
            streak(up + down, right + left)
            streak1(up + down, right + left)

            # столкновение
            if pygame.sprite.spritecollideany(bomb1, aster,
                                              collided=None) and not ne_damage:
                AnimatedSprite(load_image("2.png"), 8, 6, bomb.rect.x + 30, bomb.rect.y + 10)
                live -= 1
                ne_damage = True
                time_damage = 0
            if ne_damage:
                time_damage += 1
            if time_damage < 48:
                all_sprites.update()

            if time_damage == 155:
                ne_damage = False
                all_sprites = pygame.sprite.Group()

            # уменьшение жизни и смерть
            if live <= 0:
                job = False
                ter = True
            for i in aster_gold:
                i.rect.x -= 2
            if pygame.sprite.spritecollideany(bomb1, winner, collided=None) and not ne_damage:
                job = False
                ter = False

            # отрисовка
            aster.draw(screen)
            winner.draw(screen)
            bul.draw(screen)
            fon_asteroid.draw(screen)
            space_ship.draw(screen)
            space_ship1.draw(screen)
            all_sprites.draw(screen)
            aster_gold.draw(screen)
            pygame.font.init()
            my_font = pygame.font.SysFont('None', 80)
            player_name = my_font.render(str(nam), True, (0, 191, 255))
            screen.blit(player_name, (0, 0))

            # отрисовка жизней
            for i in range(live):
                pygame.draw.line(screen, pygame.Color('white'),
                                 (35 * (i + 2) + 15, 70),
                                 (35 * (i + 3), 70), width=20)

            pygame.display.flip()

            screen.fill(pygame.Color('black'))
            clock.tick(100)
        else:
            my_font = pygame.font.SysFont('None', 80)
            player_name = my_font.render('Pause, press Esc to continue', True, (100, 100, 100))
            screen.blit(player_name, (110, 400))
            pygame.display.flip()

            screen.fill(pygame.Color('black'))
            clock.tick(100)
    result = open('score.txt', 'a')
    result.write(nam + ' - ' + str(killed) + ' - ' + str(not ter) + '\n')
    result.close()
    if ter:
        menu1 = pygame_menu.Menu('', 1000, 1000, theme=pygame_menu.themes.THEME_DARK)

        menu1.add.label('Game over')

        menu1.add.button('Выход в меню', menu_fun)

        menu1.mainloop(screen)
    else:
        menu1 = pygame_menu.Menu('', 1000, 1000,
                                 theme=pygame_menu.themes.THEME_DARK)

        menu1.add.label('Вы выйграли')

        menu1.add.button('Выход в меню', menu_fun)

        menu1.mainloop(screen)


def menu_fun():
    menu = pygame_menu.Menu('Космо курьер', 1000, 1000, theme=pygame_menu.themes.THEME_DARK)

    name_field = menu.add.text_input('Имя:', default='Model: B № 2')

    selecting = menu.add.selector('Сложность:', [('Сложный', 1), ('Средний', 2), ('Лёгкий', 3)],
                                  selector_id='difficult')

    def start_the_game():
        selected_item = selecting.get_value()
        selected_item1 = name_field.get_value()
        leveling(selected_item[0][1], selected_item1)

    menu.add.button('Играть', start_the_game)

    menu.add.button('Выход', pygame_menu.events.EXIT)

    menu.mainloop(screen)


menu_fun()
