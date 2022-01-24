import os
import sys
import pygame
from random import randint, choice

# Изображение не получится загрузить
# без предварительной инициализации pygame
pygame.init()
pygame.mixer.init()
size = WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode(size)

# Меню/пауза
menu = pygame.Surface(screen.get_size())
menu.fill(pygame.Color("black"))
menu_slp = pygame.Surface(screen.get_size())
pygame.Surface.set_alpha(menu_slp, 100)
menu_slp.fill((100, 100, 100))

# Задержка времени
FPS = 80  # [80]
clock = pygame.time.Clock()

met_size = 40  # [40]
points = 0  # Очки
hp = 3  # Жизни [3]
planet_time = 100  # В милисекундах [100]

# Группы спрайтов
all_sprites = pygame.sprite.Group()
meteors_group = pygame.sprite.Group()
hp_group = pygame.sprite.Group()
points_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
borders = pygame.sprite.Group()
anime_group = pygame.sprite.Group()
fon_group = pygame.sprite.Group()
planet_group = pygame.sprite.Group()


# Загрузка изображений
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# Разрезка изображение на кадры
def cut_sheet(sheet, columns, rows, sc_x, sc_y):
    frames = []
    rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
    for j in range(rows):
        for i in range(columns):
            frame_location = (rect.w * i, rect.h * j)
            frames.append(pygame.transform.scale(sheet.subsurface(pygame.Rect(
                frame_location, rect.size)), (sc_x, sc_y)))
    return frames[1:], pygame.Rect(0, 0, sc_x, sc_y)


# Из кадров в анимацию
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, frames, rect):
        super().__init__(anime_group)
        self.cur_frame = 0
        self.frames = frames
        self.image = self.frames[self.cur_frame]
        self.rect = rect.move(x - rect.w // 2, y - rect.h // 2)

    def update(self):
        self.cur_frame += 1
        if self.cur_frame == len(self.frames):
            self.kill()
        else:
            self.image = self.frames[self.cur_frame]


# Внешний вид
pygame.display.set_icon(load_image("my_icon.png", -1))
bul_frames = cut_sheet(load_image("bullet.png"), 4, 4, 30, 30)
damage_frames = cut_sheet(load_image("boom.png"), 8, 6, 30, 30)
textures = {
    "meteor": load_image("asteroid.png", -1),
    "gold": load_image("gold.png", -1),
    "ufo1": load_image("ufo_model_up.png", -1),
    "ufo2": load_image("ufo_model_up1.png", -1),
    "bonus": load_image("moon.png", -1),
    "bullet": bul_frames[0][0],
    "hpbar": load_image("hpbar.png", -1),
    "planet": load_image("planeta.png")
}


# Задний фон
class Stars(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(fon_group)
        self.image = pygame.Surface((1, 1))
        self.image.fill(pygame.Color("white"))
        self.rect = self.image.get_rect().move(x, y)

    def update(self):
        y = randint(-1, 1)
        self.rect.y += y
        self.rect.x += randint(-1, 1) if y == 0 else 0


# Планета (анимация победы)
class Planet(pygame.sprite.Sprite):
    def __init__(self, time):
        super().__init__(planet_group)
        self.image = textures["planet"]
        pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        pygame.Surface.set_alpha(self.image, 200)
        self.rect = pygame.Rect(0, -self.image.get_height(), self.image.get_width(),
                                self.image.get_height())
        self.base_image = self.image
        self.time = time
        self.iter = 0
        self.y = self.rect.y

    def update(self, time_k):
        self.y += 1
        if time_k > self.time:
            # Обновление каждые [0.2] секунды (1/0.2 = 5 раз в секунду)
            self.time += 0.2
            self.iter += 1
            # Вращение планеты на [0.4] градуса (0.4 * 5 = 2 градуса в секунду)
            angle = round(self.iter * 0.4, 1)
            self.image = pygame.transform.rotate(self.base_image, angle)
            # "Пружинный механизм" для равномерного движения планеты
            self.rect = self.image.get_rect(center=self.base_image.get_rect().center)
            self.rect.y += self.y


# Инициализация и обновление самого персонажа
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player_group, all_sprites)
        self.image = textures["ufo1"]
        self.rect = self.image.get_rect().move(x - self.image.get_width() // 2,
                                               y - self.image.get_height() // 2)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        if pygame.mouse.get_focused():
            x, y = pygame.mouse.get_pos()
            self.rect = self.image.get_rect().move(x - self.image.get_width() // 2,
                                                   y - self.image.get_height() // 2)


# Пули
class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y, turn_x, turn_y):
        super().__init__(bullets_group, all_sprites)
        self.image = pygame.transform.scale(textures["bullet"], (16, 16))
        self.rect = self.image.get_rect().move(x - 8, y - 8)
        self.turn_x, self.turn_y = turn_x, turn_y
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x += self.turn_x
        self.rect.y += self.turn_y


# Границы, за которыми пропадают пули и появляются метеориты
class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.add(borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


# Метеориты
class Meteors(pygame.sprite.Sprite):
    def __init__(self, x, y, turn_x, turn_y, k):
        self.shots = 1  # Осталось выстрелов до уничтожения
        self.size = met_size
        if k == 1:
            super().__init__(meteors_group, all_sprites)
            image = "meteor"
            self.shots = 2
        elif k == 2:
            super().__init__(points_group, meteors_group, all_sprites)
            image = "gold"
        else:
            super().__init__(hp_group, meteors_group, all_sprites)
            image = "bonus"
        self.image = pygame.transform.scale(textures[image], (met_size, met_size))
        self.rect = self.image.get_rect().move(x, y)
        self.turn_x, self.turn_y = turn_x, turn_y
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        if self.shots <= 0:
            self.size -= 10
            if self.size > 0:
                self.image = pygame.transform.scale(self.image, (self.size, self.size))
                self.rect = self.image.get_rect().move((self.rect.x + 5, self.rect.y + 5))
            else:
                if self in hp_group:
                    hp_changer(1)
                elif self in points_group:
                    points_changer(1)
                self.kill()
        self.rect.x += self.turn_x
        self.rect.y += self.turn_y

    def shotted(self):
        self.shots -= 1


def spawn_meteors(count, sl):
    # Выбор начальной точки и направления
    for _ in range(count):
        where = choice(("side", "up"))
        turn_x, turn_y = randint(0, 4), randint(1, 4)
        if where == "up":
            x, y = randint(0, WIDTH), -met_size
            turn_x = -turn_x if x > WIDTH // 2 else turn_x
        else:
            x, y = choice((randint(-met_size * 2, -met_size),
                           randint(met_size + WIDTH, met_size * 2 + WIDTH))),\
                   randint(0, HEIGHT // 2)
            turn_x, turn_y = turn_y, turn_x
            turn_x = -turn_x if x > WIDTH // 2 else turn_x

        # Создание метеоритов с разными шансами для простых и для бонусных
        Meteors(x, y, turn_x, turn_y, choice((*[1] * 18, *[2] * (2 - sl), *[3] * 1)))


def hit_meteors(hits):
    for meteor, bullets in hits.items():
        for bullet in bullets:
            # Анимация взрыва пули
            AnimatedSprite(*bullet.rect.center, *bul_frames)
        # Анимация уничтожения метеора
        meteor.shotted()


# Создание границ
def create_borders():
    Border(-met_size ** 2, -met_size ** 2, WIDTH + met_size ** 2, -met_size ** 2)
    Border(-met_size ** 2, HEIGHT + met_size ** 2, WIDTH + met_size ** 2, HEIGHT + met_size ** 2)
    Border(-met_size ** 2, -met_size ** 2, -met_size ** 2, HEIGHT + met_size ** 2)
    Border(WIDTH + met_size ** 2, -met_size ** 2, WIDTH + met_size ** 2, HEIGHT + met_size ** 2)


def hp_changer(g):
    global hp
    hp += g


def points_changer(g):
    global points
    points += g


def create_fon():
    for i in range(WIDTH * HEIGHT // 500):
        Stars(randint(0, WIDTH), randint(0, HEIGHT))


# Создание экранов для паузы и меню
def pause_menu(which, sl):
    global menu
    font = pygame.font.SysFont("None", 40)
    if sl == 0:
        menu_slp.fill((150, 100, 100))
        menu.fill((10, 0, 0))
    elif sl == 1:
        menu_slp.fill((100, 100, 100))
        menu.fill(pygame.Color("black"))
    else:
        menu_slp.fill((100, 150, 100))
        menu.fill((0, 10, 0))
    if which == "pause":
        menu.blit(screen, (0, 0))
        menu.blit(menu_slp, (0, 0))
        text = ["Пауза", "",
                "Приятного чаепития!",
                "Чтобы продолжить игру, нажмите Esc", "",
                "Подсказка: Стрелять прокликом - быстрее!"]
    else:
        text = ["Меню", "",
                "Управление:",
                "Стрельба: WASD или стрелочки",
                "Движение: Мышка", "",
                "Чтобы начать - нажми пробел",
                "Чтобы выйти - нажми Esc",
                'Чтобы ввести имя - нажми на "Имя"',
                "Чтобы сохранить имя - нажми пробел",
                "Ради сохранности ваших ушей музыка будет только после первого запуска"]

        law = ["По всей галактике бушует война. Две крупнейшие торговые гильдии ведут борьбу за"
               " власть и области влияния.", "Гильдии поменьше решили воспользоваться отвлечённостью"
               " гигантов и захватить власть на их территориях.", "Глава одной из гильдий,"
               " прознав об этой подлости, решил объединиться со своим старым соперником для того,",
               "чтобы раздавить неугодных. Вы выбраны послом этой гильдии. Доставьте мирный"
               " договор.",
               "Все метеориты наносят урон.", "За ассимиляцию жёлтых ты получаешь очки.",
               "Если уничтожишь красный - получишь жизнь.",
               "Бонусные метеориты имеют меньшую плотность и ломаются легче."]
        text_x, text_y = 10, 10
        for line in law[:4]:
            menu.blit(pygame.font.SysFont("None", 25).render(line, True, pygame.Color("white")),
                      (text_x, text_y))
            text_y += 30
        menu.blit(pygame.font.SysFont("None", 50).render(
            "Сложность:", True, pygame.Color("gray")), (20, text_y + 20))
        text_y = HEIGHT - 120
        for line in law[4:]:
            menu.blit(pygame.font.SysFont("None", 25).render(line, True, pygame.Color("white")),
                      (text_x, text_y))
            text_y += 30

    text_x, text_y = WIDTH // 9 * 2, HEIGHT // 9 * 3
    for line in text:
        if line == text[0]:
            menu.blit(pygame.font.SysFont("None", 60).render(line, True, (180, 60, 60)),
                      (WIDTH // 9 * 3.5, text_y))
        elif line == text[-1]:
            menu.blit(pygame.font.SysFont("None", 25).render(line, True, (180, 60, 60)),
                      (WIDTH // 9 * 2, text_y))
        else:
            menu.blit(font.render(line, True, (180, 60, 60)), (text_x, text_y))
        text_y += 40


# Основная функция
def main(name="NiGoDa", h=3, time=-1 - planet_time, sl=1):
    global points, hp, FPS
    points = 0
    name, hp = name, h
    pygame.display.set_caption('Сверхзвуковой режим')
    running = True
    pause = False

    # Музыка
    pygame.mixer.music.load("data/music.mp3")
    pygame.mixer.music.play(10)
    pygame.mixer.music.set_volume(0.4)

    # Игрок
    player = Player(WIDTH // 2, HEIGHT // 2)
    pygame.mouse.set_visible(False)
    cursor_gone = True
    immune = 0

    # Пули
    bul_speed = 8
    holdup = 0
    hold = 40 + sl * 10  # Чем сложнее, тем быстрее стреляешь
    bul = False

    # Границы
    create_borders()

    # Фон со звёздами
    create_fon()

    # Появление метеоритов
    k = 0
    n = 14 + sl * 2  # Каждый n кадр [16]
    count = 4  # Метеоритов за раз [4]

    time_now = pygame.time.get_ticks() // 100
    last_time, false_time = 0, time_now

    # Основной цикл
    while running:
        time_now = pygame.time.get_ticks() // 100
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and not pause:
                if event.key in (pygame.K_UP, pygame.K_w):
                    bul = (0, -bul_speed)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    bul = (0, bul_speed)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    bul = (-bul_speed, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    bul = (bul_speed, 0)
            elif event.type == pygame.KEYUP and not pause:
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
                                 pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d):
                    bul = False
                    holdup //= 2
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not pause:
                        pause = True
                        cursor_gone = True
                        pygame.mouse.set_visible(True)
                        last_time = time_now
                        pause_menu("pause", sl)
                    else:
                        pause = False
                        pygame.mouse.set_visible(False)
                        false_time += time_now - last_time

        if time_now - false_time == time and len(planet_group) == 0 and not pause:
            Planet(time)

        # Коммит = режим бога
        if (hp == 0 or time_now - false_time == time + planet_time) and not pause:
            break

        if holdup == 0 and bul:
            Bullets(*player.rect.center, *bul)
            holdup = hold
        # 'Убийство' пуль, вышедших за рамки
        pygame.sprite.groupcollide(bullets_group, borders, True, False)
        # 'Убийство' метеоритов, вышедших за рамки
        pygame.sprite.groupcollide(meteors_group, borders, True, False)

        # Метеориты
        if k == n and len(planet_group) == 0:
            k = 0
            spawn_meteors(count, sl)

        # Попадание пуль по метеоритам
        hit_meteors(pygame.sprite.groupcollide(meteors_group, bullets_group, False, True))

        # Столковение с астероидами
        warning = pygame.sprite.spritecollide(player, meteors_group, False)
        if warning:
            for meteor in warning:
                if pygame.sprite.collide_mask(player, meteor) and immune == 0:
                    hp_changer(-1)
                    immune = 100 + sl * 20  # Время на передышку
                    AnimatedSprite(*player.rect.center, *damage_frames)

        # Отрисовка
        # Нажата ли пауза
        if not pause:
            screen.fill(pygame.Color("black"))
            fon_group.draw(screen)

            k += 1
            immune -= 1 if immune > 0 else 0
            holdup -= 1 if holdup > 0 else 0

            # Постановка курсора к кораблю
            if cursor_gone and pygame.mouse.get_focused():
                pygame.mouse.set_pos(player.rect.center)
            cursor_gone = not pygame.mouse.get_focused()

            # Интерфейс
            screen.blit(textures["hpbar"], (0, 0))
            screen.blit(pygame.font.SysFont('None', 80).render(name, True, (0, 191, 255)), (0, 0))
            screen.blit(pygame.font.SysFont('None', 40).render(
                f"Время: {round((time_now - false_time) / 10)}", True, (100, 191, 255)),
                (0, 90))
            for i in range(hp):
                pygame.draw.line(screen, pygame.Color(255, 255, 255),
                                 (35 * (i + 2) + 15, 70),
                                 (35 * (i + 3), 70), width=20)
            if k % 2 == 0:
                anime_group.update()
                fon_group.update()
                planet_group.update(time_now - false_time)
                player.image = textures["ufo1"] if player.image == textures["ufo2"] else\
                    textures["ufo2"]
            all_sprites.update()
            planet_group.draw(screen)
            meteors_group.draw(screen)
            bullets_group.draw(screen)
            player_group.draw(screen)
            anime_group.draw(screen)
        else:
            screen.blit(menu, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)
    pygame.mouse.set_visible(True)
    for sprite in (*all_sprites, *planet_group, *fon_group, *anime_group):
        sprite.kill()
    return points, hp, time_now - false_time == time + planet_time


# Функция для инициализации меню
def start_end_screen():
    eng_rus = "qwertyuiop[]asdfghjkl;'zxcvbnm,.`", "йцукенгшщзхъфывапролджэячсмитьбюё"  # 33
    rus = True
    n = ["NiGoDa", 3, 150, 1]  # В милисекундах [1800 = 3 минуты]
    running = True
    result = ()
    t_x, t_y = WIDTH // 9, HEIGHT // 9 * 7
    buttons = (
        ("Лёгкая", (pygame.font.SysFont("None", 50).render("Лёгкая", True, pygame.Color("gray")),
                    (240, 150))),
        ("Средняя", (pygame.font.SysFont("None", 50).render("Средняя", True, pygame.Color("gray")),
                     (380, 150))),
        ("Сложная", (pygame.font.SysFont("None", 50).render("Сложная", True, pygame.Color("gray")),
                     (560, 150))))
    selected = buttons[1][1][0].get_rect(), buttons[1][1][1]
    name_btn = pygame.font.SysFont("None", 50).render("Имя:", True, pygame.Color("gray")), (143, 230)
    vvod = False
    name = n[0]
    while running:
        pygame.display.set_caption("Меню игры, созданной для совместного проекта")
        pause_menu("menu", n[3])
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif vvod:
                    if event.key == pygame.K_RETURN:
                        vvod = False
                        n[0] = name
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif event.key == pygame.K_LALT and\
                            (pygame.key.get_pressed()[pygame.K_LSHIFT] or
                             pygame.key.get_pressed()[pygame.K_RSHIFT]):
                        rus = False if rus else True
                    elif event.key in range(0x110000):
                        key = chr(event.key)
                        if rus and key in eng_rus[0]:
                            key = eng_rus[1][eng_rus[0].index(key)]
                        if pygame.key.get_pressed()[pygame.K_LSHIFT] or \
                                pygame.key.get_pressed()[pygame.K_RSHIFT]:
                            if key in "1234567890-=":
                                key = '!@#$%^&*()_+'["1234567890-=".index(key)]
                            else:
                                key = key.upper()
                            if rus and key in '"№;:?':
                                key = '"№;:?'['@#$^&'.index(key)]
                        name += key
                elif event.key == pygame.K_SPACE:
                    result = main(*n)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, but in buttons:
                    if but[0].get_rect().move(but[1]).collidepoint(event.pos):
                        n[3] = ("Сложная", "Средняя", "Лёгкая").index(i)
                        selected = but[0].get_rect(), but[1]
                if name_btn[0].get_rect().move(name_btn[1]).collidepoint(event.pos):
                    vvod = True
                    name = ""

        if result:
            p, heal, win = result
            if win:
                itog = f"{name} доставил послание и по пути заработал {p} золота,"
                if heal == n[1]:
                    heal = "не угробя при этом корабль."
                elif heal < n[1]:
                    heal = f"потеряв при этом {n[1] - heal} прочности корабля."
                else:
                    heal = f"мистическим образом при этом нарастив {heal - n[1]} слоёв брони."
            else:
                itog, heal = f"{name} не выжил. На его обломках осталось {p} золота.", ""
            menu.blit(pygame.font.SysFont("None", 40).render(
                itog, True, pygame.Color("orange")), (t_x, t_y))
            menu.blit(pygame.font.SysFont("None", 40).render(
                heal, True, pygame.Color("orange")), (t_x, t_y + 45))

        for i in buttons:
            menu.blit(*i[1])
        menu.blit(*name_btn)
        sel_p = pygame.Surface(selected[0].size)
        sel_p.fill((255, 0, 0))
        pygame.Surface.set_alpha(sel_p, 120)
        menu.blit(sel_p, selected[1])
        if vvod:
            sel_p = pygame.Surface(name_btn[0].get_rect().size)
            sel_p.fill((255, 0, 0))
            pygame.Surface.set_alpha(sel_p, 120)
            menu.blit(sel_p, name_btn[1])
        menu.blit(pygame.font.SysFont("None", 50).render(name, True, pygame.Color("gray")),
                  (225, 230))

        screen.blit(menu, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == '__main__':
    start_end_screen()
