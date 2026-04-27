import pygame
import random
import sys

pygame.init()

#  Константы
CELL        = 20          # размер одной клетки в пикселях
COLS        = 25          # количество колонок
ROWS        = 25          # количество строк
PANEL_H     = 60          # высота панели с HUD сверху

SCREEN_W    = CELL * COLS
SCREEN_H    = CELL * ROWS + PANEL_H

FPS_START   = 6           # начальная скорость (кадров/сек)
FPS_STEP    = 1           # прибавка скорости за каждый уровень
FOOD_PER_LVL = 3          # сколько еды нужно съесть для следующего уровня

# Цвета
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
BG_COLOR    = (15,  20,  30)    # тёмный фон поля
GRID_COLOR  = (25,  32,  45)    # цвет сетки
PANEL_COLOR = (10,  14,  22)    # цвет панели HUD

SNAKE_HEAD  = (50,  220,  80)
SNAKE_BODY  = (30,  160,  55)
SNAKE_OUT   = (20,  100,  35)   # обводка змеи

FOOD_COLOR  = (255,  70,  70)
FOOD_OUT    = (180,  20,  20)

WALL_COLOR  = (80,   90, 110)
WALL_OUT    = (50,   60,  80)

TEXT_COLOR  = (200, 210, 230)
GOLD        = (255, 210,   0)
LEVEL_COLOR = (100, 200, 255)

#  Создание окна
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Snake 🐍")
clock  = pygame.time.Clock()

# Шрифты
font_big    = pygame.font.SysFont("Arial", 42, bold=True)
font_med    = pygame.font.SysFont("Arial", 26, bold=True)
font_small  = pygame.font.SysFont("Arial", 18)


#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ

def cell_rect(col, row):
    """Возвращает pygame.Rect для клетки (col, row) с учётом панели сверху."""
    return pygame.Rect(col * CELL, row * CELL + PANEL_H, CELL, CELL)


def draw_cell(surface, col, row, color, outline=None, radius=4):
    """Рисует закруглённый прямоугольник в клетке (col, row)."""
    r = cell_rect(col, row).inflate(-2, -2)
    pygame.draw.rect(surface, color,   r, border_radius=radius)
    if outline:
        pygame.draw.rect(surface, outline, r, width=2, border_radius=radius)


def draw_grid(surface):
    """Рисует фон и тонкую сетку игрового поля."""
    # Заливка поля
    field_rect = pygame.Rect(0, PANEL_H, SCREEN_W, SCREEN_H - PANEL_H)
    pygame.draw.rect(surface, BG_COLOR, field_rect)
    # Горизонтальные линии
    for r in range(ROWS + 1):
        y = r * CELL + PANEL_H
        pygame.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_W, y))
    # Вертикальные линии
    for c in range(COLS + 1):
        x = c * CELL
        pygame.draw.line(surface, GRID_COLOR, (x, PANEL_H), (x, SCREEN_H))


def draw_hud(surface, score, level, food_eaten, food_per_lvl, fps):
    """Рисует панель HUD: очки, уровень, прогресс-бар."""
    pygame.draw.rect(surface, PANEL_COLOR, (0, 0, SCREEN_W, PANEL_H))
    pygame.draw.line(surface, WALL_COLOR, (0, PANEL_H), (SCREEN_W, PANEL_H), 2)

    # Очки
    s = font_med.render(f"Score: {score}", True, TEXT_COLOR)
    surface.blit(s, (12, 10))

    # Уровень
    lv = font_med.render(f"Level: {level}", True, LEVEL_COLOR)
    surface.blit(lv, (12, 34))

    # Прогресс до следующего уровня (справа)
    bar_w   = 160
    bar_h   = 14
    bar_x   = SCREEN_W - bar_w - 12
    bar_y   = 12
    filled  = int(bar_w * (food_eaten % food_per_lvl) / food_per_lvl)

    pygame.draw.rect(surface, (40, 50, 70),  (bar_x, bar_y, bar_w, bar_h), border_radius=6)
    if filled > 0:
        pygame.draw.rect(surface, GOLD, (bar_x, bar_y, filled, bar_h), border_radius=6)
    pygame.draw.rect(surface, WALL_COLOR, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=6)

    label = font_small.render("Next level", True, TEXT_COLOR)
    surface.blit(label, (bar_x, bar_y + bar_h + 3))

    # Скорость
    sp = font_small.render(f"Speed: {fps}", True, (150, 160, 180))
    surface.blit(sp, (SCREEN_W - 100, bar_y + bar_h + 3))


def show_overlay(surface, title, lines):
    """Рисует полупрозрачный оверлей с заголовком и строками текста."""
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))

    t = font_big.render(title, True, WHITE)
    surface.blit(t, t.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 50)))

    for i, line in enumerate(lines):
        s = font_small.render(line, True, (200, 210, 230))
        surface.blit(s, s.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 10 + i * 26)))


def random_free_pos(snake_body, walls):
    """
    Генерирует случайную позицию еды, которая не совпадает
    со змеёй, стенами или границей поля.
    """
    occupied = set(snake_body) | set(walls)
    while True:
        col = random.randint(1, COLS - 2)
        row = random.randint(1, ROWS - 2)
        if (col, row) not in occupied:
            return col, row


def generate_walls(level):
    """
    Генерирует набор внутренних стен в зависимости от уровня.
    Уровень 1 — стен нет; с уровня 2 добавляются препятствия.
    """
    walls = set()
    if level < 2:
        return walls

    # Горизонтальные «заграждения» посередине
    mid_r = ROWS // 2
    length = min(4 + level * 2, COLS - 6)
    start_c = (COLS - length) // 2

    for c in range(start_c, start_c + length):
        walls.add((c, mid_r))

    if level >= 3:
        # Вертикальные столбики
        mid_c = COLS // 2
        for r in range(4, ROWS - 4, 3):
            walls.add((mid_c - 6, r))
            walls.add((mid_c + 6, r))

    if level >= 4:
        # Дополнительные блоки по углам поля
        for c in range(3, 7):
            walls.add((c, 5))
            walls.add((COLS - c - 1, ROWS - 6))

    return walls


#  ОСНОВНОЙ ИГРОВОЙ ЦИКЛ

def game_loop():
    # Начальное состояние
    level        = 1
    score        = 0
    food_eaten   = 0          # всего съедено (для уровней)
    current_fps  = FPS_START

    # Змея — список клеток (col, row), голова первая
    snake = [(COLS // 2, ROWS // 2),
             (COLS // 2 - 1, ROWS // 2),
             (COLS // 2 - 2, ROWS // 2)]

    direction     = (1, 0)    # движение вправо
    next_dir      = direction # буферизованное следующее направление
    walls         = generate_walls(level)
    food = {
        "pos": random_free_pos(snake, walls),
        "weight": random.choice([1, 2, 3]),   # разный вес
        "timer": random.randint(100, 200)     # время жизни
    }

    started       = False
    game_over     = False
    level_up_msg  = 0         # кадры показа сообщения об уровне

    while True:
        clock.tick(current_fps)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Запуск / рестарт
                if event.key == pygame.K_SPACE:
                    if not started:
                        started = True
                    elif game_over:
                        game_loop()
                        return

                # Управление змеёй (нельзя развернуться на 180°)
                if event.key == pygame.K_UP    and direction != (0,  1): next_dir = (0, -1)
                if event.key == pygame.K_DOWN  and direction != (0, -1): next_dir = (0,  1)
                if event.key == pygame.K_LEFT  and direction != (1,  0): next_dir = (-1, 0)
                if event.key == pygame.K_RIGHT and direction != (-1, 0): next_dir = (1,  0)

        # Стартовый экран
        if not started:
            draw_grid(screen)
            draw_hud(screen, score, level, food_eaten, FOOD_PER_LVL, current_fps)
            show_overlay(screen, "SNAKE 🐍",
                         ["Arrow keys — move", "SPACE — start"])
            pygame.display.flip()
            continue

        # Экран Game Over
        if game_over:
            draw_grid(screen)
            for w in walls:
                draw_cell(screen, *w, WALL_COLOR, WALL_OUT)
            draw_cell(screen, *food, FOOD_COLOR, FOOD_OUT)
            for i, seg in enumerate(snake):
                c = SNAKE_HEAD if i == 0 else SNAKE_BODY
                draw_cell(screen, *seg, c, SNAKE_OUT)
            draw_hud(screen, score, level, food_eaten, FOOD_PER_LVL, current_fps)
            show_overlay(screen, "GAME OVER",
                         [f"Score: {score}   Level: {level}",
                          "SPACE — restart"])
            pygame.display.flip()
            continue

        # Движение змеи
        direction  = next_dir
        head_c, head_r = snake[0]
        new_head   = (head_c + direction[0], head_r + direction[1])

        # Проверка столкновения со стеной поля (граница)
        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            game_over = True
            continue

        # Проверка столкновения с телом змеи
        if new_head in snake[1:]:
            game_over = True
            continue

        # Проверка столкновения с внутренними стенами
        if new_head in walls:
            game_over = True
            continue

        # Змея съела еду
        if new_head == food["pos"]:
            snake.insert(0, new_head)   # растём (не убираем хвост)
            score += 10 * level * food["weight"]   # очки зависят от веса еды
            food_eaten  += 1

            # Повышение уровня
            if food_eaten % FOOD_PER_LVL == 0:
                level        += 1
                current_fps   = FPS_START + (level - 1) * FPS_STEP
                walls         = generate_walls(level)
                level_up_msg  = current_fps * 2   # показываем ~2 секунды

            food = {
                "pos": random_free_pos(snake, walls),
                "weight": random.choice([1, 2, 3]),
                "timer": random.randint(100, 200)
            }

        else:
            # Обычное движение: добавляем голову, убираем хвост
            snake.insert(0, new_head)
            snake.pop()
            
            # уменьшаем время жизни еды
            food["timer"] -= 1

            # если время закончилось — создаём новую еду
            if food["timer"] <= 0:
                food = {
                    "pos": random_free_pos(snake, walls),
                    "weight": random.choice([1, 2, 3]),
                    "timer": random.randint(100, 200)
                }    

        if level_up_msg > 0:
            level_up_msg -= 1

        # Отрисовка
        draw_grid(screen)

        # Стены
        for w in walls:
            draw_cell(screen, *w, WALL_COLOR, WALL_OUT, radius=2)

        # Еда
        food_pos = food["pos"]

        # цвет зависит от веса
        if food["weight"] == 1:
            color = (255, 70, 70)
        elif food["weight"] == 2:
            color = (255, 165, 0)
        else:
            color = (255, 255, 0)

        food_r = cell_rect(*food_pos).inflate(-4, -4)
        pygame.draw.ellipse(screen, color, food_r)
        pygame.draw.ellipse(screen, FOOD_OUT, food_r, 2)

        # Змея
        for i, seg in enumerate(snake):
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            draw_cell(screen, *seg, color, SNAKE_OUT)

        # HUD
        draw_hud(screen, score, level, food_eaten, FOOD_PER_LVL, current_fps)

        # Сообщение о повышении уровня
        if level_up_msg > 0:
            msg = font_med.render(f"⬆  LEVEL {level}!", True, GOLD)
            screen.blit(msg, msg.get_rect(center=(SCREEN_W // 2, PANEL_H + 40)))

        pygame.display.flip()


#  Точка входа
if __name__ == "__main__":
    game_loop()