import pathlib
import random

from typing import List, Optional, Tuple

Cell = Tuple[int, int]
Cells = List[int]
Grid = List[Cells]


class GameOfLife:
    def __init__(
            self,
            size: Tuple[int, int],
            randomize: bool = True,
            max_generations: Optional[float] = float('inf')) -> None:
        # Размер клеточного поля
        self.rows, self.cols = size
        # Предыдущее поколение клеток
        self.prev_generation = self.create_grid()
        # Текущее поколение клеток
        self.curr_generation = self.create_grid(randomize=randomize)
        # Максимальное число поколений
        self.max_generations = max_generations
        # Текущее число поколений
        self.n_generation = 1

    def create_grid(self, randomize: bool = False) -> Grid:
        grid = [[0 for _ in range(self.cols)]
                for _ in range(self.rows)]
        if randomize:
            for i in range(self.rows):
                for j in range(self.cols):
                    grid[i][j] = random.randint(0, 1)
        return grid

    def get_neighbours(self, cell: Cell) -> Cells:
        neighbours = []
        i, j = cell
        neighbour_coordinate = [(i, j - 1), (i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                                (i, j + 1), (i + 1, j + 1), (i + 1, j), (i + 1, j - 1)]
        for y, x in neighbour_coordinate:
            if 0 <= y < self.rows and 0 <= x < self.cols:
                neighbours.append(self.curr_generation[y][x])
        return neighbours

    def get_next_generation(self) -> Grid:
        # Copy from previous assignment
        new_grid = self.create_grid()
        for i in range(self.rows):
            for j in range(self.cols):
                neighbours = self.get_neighbours((i, j))
                if self.curr_generation[i][j] == 0:
                    if sum(neighbours) == 3:
                        new_grid[i][j] = 1
                else:
                    if 2 <= sum(neighbours) <= 3:
                        new_grid[i][j] = 1
        return new_grid

    def step(self) -> None:
        """
        Выполнить один шаг игры.
        """
        if not self.is_max_generations_exceed:
            self.prev_generation = self.curr_generation
            self.curr_generation = self.get_next_generation()
            self.n_generation += 1

    @property
    def is_max_generations_exceed(self) -> bool:
        """
        Не превысило ли текущее число поколений максимально допустимое.
        """
        return self.n_generation >= self.max_generations

    @property
    def is_changing(self) -> bool:
        """
        Изменилось ли состояние клеток с предыдущего шага.
        """
        return self.prev_generation != self.curr_generation

    @staticmethod
    def from_file(filename: pathlib.Path) -> 'GameOfLife':
        """
        Прочитать состояние клеток из указанного файла.
        """
        with open(filename) as file:
            grid = []
            file_lines = file.readlines()
            for i in range(len(file_lines)):
                grid.append([int(cell) for cell in list(file_lines[i])])

        rows, cols = len(grid), len(grid[0])
        game = GameOfLife((rows, cols))
        game.curr_generation = grid
        return game

    def save(self, filename: pathlib.Path) -> None:
        """
        Сохранить текущее состояние клеток в указанный файл.
        """
        with open(filename) as file:
            for row in self.curr_generation:
                line = [str(cell) for cell in row]
                file.write(''.join(line))
                file.write('\n')
