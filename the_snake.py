from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Собственные цвета объектов:
BOARD_BACKGROUND_COLOR = (12, 24, 18)
BORDER_COLOR = (64, 140, 110)
APPLE_COLOR = (220, 60, 50)
POISON_COLOR = (160, 80, 200)
ROCK_COLOR = (90, 95, 100)
SNAKE_COLOR = (70, 200, 90)

# Скорость движения змейки:
SPEED = 5
SPEED_MAX = 35

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


def get_random_position(occupied=()):
    """Возвращает случайную свободную клетку на поле."""
    occupied = set(occupied)
    while True:
        position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )
        if position not in occupied:
            return position


class GameObject:
    """Базовый класс игрового объекта."""

    def __init__(self, position=None, body_color=None):
        """Инициализирует позицию и цвет объекта."""
        if position is None:
            position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс яблока — еды для змейки."""

    def __init__(self, body_color=APPLE_COLOR):
        """Задаёт цвет яблока и случайную позицию на поле."""
        super().__init__(body_color=body_color)
        self.randomize_position()

    def randomize_position(self, occupied=()):
        """Устанавливает случайную позицию яблока на игровом поле."""
        self.position = get_random_position(occupied)


class Poison(Apple):
    """«Неправильная» еда — уменьшает длину змейки."""

    def __init__(self):
        """Создаёт ядовитую еду с отдельным цветом."""
        super().__init__(body_color=POISON_COLOR)


class Rock(GameObject):
    """Препятствие: при столкновении змейка сбрасывается."""

    def __init__(self):
        """Размещает камень в случайной клетке."""
        super().__init__(body_color=ROCK_COLOR)
        self.randomize_position()

    def randomize_position(self, occupied=()):
        """Устанавливает случайную позицию камня."""
        self.position = get_random_position(occupied)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализирует змейку в центре поля."""
        super().__init__(body_color=body_color)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.removed = []

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Перемещает змейку на один сегмент в текущем направлении."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        self.position = new_head
        self.removed = []
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
            self.removed.append(self.last)
        else:
            self.last = None

    def shrink(self):
        """Уменьшает длину змейки на один сегмент."""
        if self.length > 1:
            self.length -= 1
            removed = self.positions.pop()
            self.last = removed
            self.removed.append(removed)

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.position = self.positions[0]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None
        self.removed = []

    def draw(self):
        """Отрисовывает змейку на игровой поверхности."""
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        for position in self.removed:
            last_rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для управления змейкой и скоростью."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def occupied_cells(snake, *objects):
    """Собирает занятые клетки: сегменты змейки и позиции объектов."""
    cells = list(snake.positions)
    for obj in objects:
        cells.append(obj.position)
    return cells


def main():
    """Запускает основной игровой цикл."""
    pygame.init()
    snake = Snake()
    apple = Apple()
    poison = Poison()
    rock = Rock()

    # Разводим объекты по разным клеткам при старте.
    apple.randomize_position(snake.positions)
    poison.randomize_position(occupied_cells(snake, apple))
    rock.randomize_position(occupied_cells(snake, apple, poison))
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        # Базовая скорость + бонус за длину (игра ускоряется по мере роста).
        current_speed = min(SPEED_MAX, SPEED + snake.length // 2)
        clock.tick(current_speed)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        head = snake.get_head_position()

        if head == apple.position:
            snake.length += 1
            apple.randomize_position(
                occupied_cells(snake, poison, rock),
            )

        elif head == poison.position:
            snake.shrink()
            poison.randomize_position(
                occupied_cells(snake, apple, rock),
            )

        elif head == rock.position:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)
            poison.randomize_position(occupied_cells(snake, apple))
            rock.randomize_position(occupied_cells(snake, apple, poison))

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)

        snake.draw()
        apple.draw()
        poison.draw()
        rock.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
