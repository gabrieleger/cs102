import pygame
from pygame.locals import *
import argparse

from life import GameOfLife
from ui import UI


class GUI(UI):

    def __init__(self, life: GameOfLife, cell_size: int = 10, speed: int = 10) -> None:
        super().__init__(life)
        self.cell_size = cell_size
        self.speed = speed

        self.width = self.life.cols * cell_size
        self.height = self.life.rows * cell_size
        self.screen = pygame.display.set_mode((self.width, self.height))

    def draw_lines(self) -> None:
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                             (0, y), (self.width, y))

    def draw_grid(self) -> None:
        for i in range(self.life.rows):
            for j in range(self.life.cols):
                if self.life.curr_generation[i][j] == 1:
                    pygame.draw.rect(self.screen, pygame.Color('green'),
                                     ((1 + j * self.cell_size, 1 + i * self.cell_size), (self.cell_size - 1, self.cell_size - 1)))

    def run(self) -> None:
        # Copy from previous assignment
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption('Game of Life')
        self.screen.fill(pygame.Color('white'))

        game_paused = False
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        if game_paused:
                            game_paused = False
                        else:
                            game_paused = True
                if event.type == MOUSEBUTTONDOWN:
                    if game_paused:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        x, y = mouse_x // self.cell_size, mouse_y // self.cell_size
                        if self.life.curr_generation[y][x] == 0:
                            self.life.curr_generation[y][x] = 1
                        else:
                            self.life.curr_generation[y][x] = 0

            self.screen.fill(pygame.Color('white'))
            self.draw_lines()
            self.draw_grid()

            if not game_paused:
                if not self.life.is_max_generations_exceed:
                    self.life.step()
                else:
                    pygame.display.set_caption('Game of Life | Максимальное количество шагов достигнуто')
            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Game of life')
    parser.add_argument('--width', type=int, default=640, help='Ширина окна игры в пикселях')
    parser.add_argument('--height', type=int, default=480, help='Высота окна игры в пикселях')
    parser.add_argument('--cell-size', type=int, default=10, help='Размер одной клетки в пикселях')
    parser.add_argument('--max-generations', default=float('inf'), type=int, help='Максимальное количество шагов игры')
    args = parser.parse_args()
    game = GameOfLife((args.height // args.cell_size, args.width // args.cell_size), max_generations=args.max_generations)
    gui = GUI(game, args.cell_size)
    gui.run()
