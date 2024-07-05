import pygame
import random

# Инициализация Pygame
pygame.init()

# Настройки экрана
SCREEN_WIDTH = 450
SCREEN_HEIGHT = 900
GRID_SIZE = 30
COLUMNS = SCREEN_WIDTH // GRID_SIZE
ROWS = SCREEN_HEIGHT // GRID_SIZE

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Путь к файлам изображений
IMAGES_PATH = 'images\\'
BACKGROUND_IMG = IMAGES_PATH + 'background-tetris.png'
SHAPE_IMAGES = {
    'I': IMAGES_PATH + 'blue.png',
    'O': IMAGES_PATH + 'cian.png',
    'T': IMAGES_PATH + 'green.png',
    'S': IMAGES_PATH + 'pink.png',
    'Z': IMAGES_PATH + 'purple.png',
    'J': IMAGES_PATH + 'red.png',
    'L': IMAGES_PATH + 'yellow.png'
}

# Определение фигур и их вращений
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]  # L
]

# Соответствие фигур и их идентификаторов
SHAPE_IDS = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']


class Tetromino:
    def __init__(self, shape, shape_id):
        self.shape = shape
        self.shape_id = shape_id
        self.image = pygame.image.load(SHAPE_IMAGES[shape_id])
        self.x = COLUMNS // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        ''' Поворот фигуры'''
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def draw(self, surface):
        ''' Отрисовка фигуры'''
        # Проьегаем по матрице фигуры двумя циклами
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    # Отрисовка фигуры
                    surface.blit(
                        self.image,
                        pygame.Rect(
                            (self.x + j) * GRID_SIZE,
                            (self.y + i) * GRID_SIZE,
                            GRID_SIZE,
                            GRID_SIZE
                        )
                    )


def create_grid(locked_positions={}):
    ''' Создание сетки игрового поля с учетом заблокированных ячеек'''
    # Создание пустой строки
    grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    # Заполнение сетки заблокированными позициями
    for (x, y), shape_id in locked_positions.items():
        image = pygame.image.load(SHAPE_IMAGES[shape_id])
        grid[y][x] = image
    # Возвращает сетку
    return grid


def valid_space(shape, grid):
    '''Проверяет, можно ли разместить фигуру в текущем положении
    без пересечений с другими фигурами или выхода за границы игрового поля'''
    # Создание списка допустимых позиций
    accepted_positions = [[(j, i) for j in range(COLUMNS) if grid[i][j] ==
                           BLACK] for i in range(ROWS)]
    # Преобразование двухмерного списка в один список допустимых позицый
    accepted_positions = [j for sub in accepted_positions for j in sub]
    # Преобразование текущей формы фигуры в список ее координат на сетке.
    formatted_shape = convert_shape_format(shape)
    # Проверка координат на допустимость
    for pos in formatted_shape:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True


def convert_shape_format(shape):
    '''Преобразует форму фигуры в список координат на сетке игрового поля.
    Эти координаты используются для проверки допустимости позиции фигуры
    (например, при движении или вращении)
    и для отображения фигуры на экране.'''
    # Инициализируем список позицый
    positions = []
    # Проход по строкам - получаем индекс строки и саму строку
    for i, line in enumerate(shape.shape):
        # Прохоим по колонкам
        for j, column in enumerate(line):
            # Если ячека занята, то она добавляется в список позиций
            if column:
                positions.append((shape.x + j, shape.y + i))
    # Возвращения списка всех занятых позиций
    return positions


def check_lost(positions):
    ''' Функция check_lost проверяет, достигли ли заблокированные фигуры
    верхней части игрового поля, что является признаком проигрыша в игре
    Тетрис.'''
    # Перебор позиций
    for pos in positions:
        x, y = pos
        # Проверка на достижение верхней границы
        if y < 1:
            return True
    return False


def clear_rows(grid, locked):
    '''Функция clear_rows удаляет полностью заполненные строки из сетки и
    обновляет позиции заблокированных фигур'''
    # Счетчик очищенных строк
    increment = 0
    # Проход по строкам сетки в обратном порядке
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        # Проверка заполненности строк
        if BLACK not in row:
            # Удаление заполненной строки
            increment += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    # Обновление позиций заюлокированных фигур
    if increment > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + increment)
                locked[newKey] = locked.pop(key)
    # Возвращает количество очищенных строк
    return increment


def draw_window(surface, grid, background, score):
    '''Отвечает за отрисовку всего игрового окна, включая фон, сетку, фигуры
    и текущий счет. Она используется для обновления отображения игры на экране
    при каждом кадре.'''
    # Отрисовка фона
    surface.blit(background, (0, 0))
    # Отрисовка ячеек сетки
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] != BLACK:
                surface.blit(grid[i][j], (j * GRID_SIZE, i * GRID_SIZE))
    pygame.draw.rect(surface, WHITE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 5)

    # Отображение счета
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', 1, WHITE)
    surface.blit(label, (10, 10))


def main():
    # Игровая поверхность
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Тетрис')
    # Словарь заблокированных позиций
    locked_positions = {}
    # Игровое поле
    grid = create_grid(locked_positions)
    # Флаг, говорящий о необходимости смены текущей фигуры
    change_piece = False
    # Флаг, указывающий, продолжаетя ли игра
    run = True
    # Текущая фигура
    current_piece = Tetromino(random.choice(SHAPES), random.choice(SHAPE_IDS))
    # Следующая фигура
    next_piece = Tetromino(random.choice(SHAPES), random.choice(SHAPE_IDS))
    # Объект для управлением временем и FPS
    clock = pygame.time.Clock()
    # Переменная для отслеживания времени падения фигуры
    fall_time = 0
    # Счет игрока
    score = 0
    # Картинка фона
    background = pygame.image.load(BACKGROUND_IMG)
    # Основной цикл игры
    while run:
        grid = create_grid(locked_positions)
        fall_speed = 0.27
        grid = create_grid(locked_positions)

        fall_time += clock.get_rawtime()
        clock.tick()
        # Управление движением и вращением фигуры
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
        # Обработка событий клавиатуры и мыши
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        current_piece.rotate()
                        current_piece.rotate()
                        current_piece.rotate()
                if event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                current_piece.rotate()
                if not valid_space(current_piece, grid):
                    current_piece.rotate()
                    current_piece.rotate()
                    current_piece.rotate()
        # Отрисовка текущей и следующей фигур, обновление игрового окна
        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.image

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.shape_id

            current_piece = next_piece
            next_piece = Tetromino(random.choice(SHAPES),
                                   random.choice(SHAPE_IDS))
            change_piece = False

            # Очистка строк и обновление счета
            lines_cleared = clear_rows(grid, locked_positions)
            # Начисляем 100 очков за каждую очищенную строку
            score += lines_cleared * 100
        # Отрисовка игрового окна
        draw_window(surface, grid, background, score)
        current_piece.draw(surface)
        pygame.display.update()
        # Если игрок проиграл
        if check_lost(locked_positions):
            run = False

    pygame.display.quit()
    quit()


if __name__ == '__main__':
    main()
