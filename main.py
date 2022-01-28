import Kirams
import Supersonic_mode


def run():
    # data Ник, хп, время, сложность, режим
    # result Очки, хп, прошёл ли
    data = ["NiGoDa", 3, 1200, 1, 0]  # В милисекундах [1800 = 3 минуты]
    running = True
    while running:
        running, data = Supersonic_mode.start_screen(data)
        if not running:
            Supersonic_mode.terminate()

        # Музыка
        if not Supersonic_mode.pygame.mixer.music.get_busy():
            Supersonic_mode.music_changer(Supersonic_mode.music)

        if data[4] == 1:
            result = Supersonic_mode.main(*data[:-1])
        elif data[4] == 2:
            result = Kirams.leveling(abs(data[3] + 1), data[0])
        else:
            result = Kirams.leveling(abs(data[3] + 1), data[0])
            if result[2]:
                dat_copy = data[:]
                dat_copy[1] = 2 + result[1]
                result, result1 = [*Supersonic_mode.main(*dat_copy[:-1])], result
                result[0] = result1[0] + result[0]

        running = Supersonic_mode.end_screen(data, result)

        Supersonic_mode.pygame.display.flip()
        Supersonic_mode.clock.tick(Supersonic_mode.FPS)

    Supersonic_mode.pygame.quit()


if __name__ == '__main__':
    run()
