import time
import curses

import argparse

from life import GameOfLife
from ui import UI


class Console(UI):

    def __init__(self, life: GameOfLife) -> None:
        super().__init__(life)

    def draw_borders(self, screen) -> None:
        """ Отобразить рамку. """
        screen.border(0)

    def draw_grid(self, screen) -> None:
        """ Отобразить состояние клеток. """
        for i in range(len(self.life.curr_generation)):
            for j in range(len(self.life.curr_generation[0])):
                if self.life.curr_generation[i][j] != 0:
                    try:
                        screen.addstr(i + 1, j + 1, '*')
                    except curses.error:
                        pass

    def run(self) -> None:
        screen = curses.initscr()
        curses.curs_set(0)

        running = True
        while running:
            screen.clear()
            self.draw_borders(screen)
            self.draw_grid(screen)
            self.life.step()

            if self.life.is_max_generations_exceed:
                running = False

            screen.refresh()
            time.sleep(0.02)

        time.sleep(2)
        curses.endwin()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Game of life in console')
    parser.add_argument('--rows', type=int, default=15, help='Высота поля в клетках')
    parser.add_argument('--cols', type=int, default=100, help='Ширина поля в клетках')
    parser.add_argument('--max-generations', default=200, type=int, help='Максимальное количество шагов игры')
    args = parser.parse_args()
    game = GameOfLife((args.rows, args.cols), max_generations=args.max_generations)
    console = Console(game)
    console.run()
