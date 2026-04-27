import pygame
import random
import sys
import json

from db import save_result, get_top_10, get_personal_best

pygame.init()

CELL = 20
COLS = 25
ROWS = 25
PANEL_H = 60

SCREEN_W = CELL * COLS
SCREEN_H = CELL * ROWS + PANEL_H

FPS_START = 6
FPS_STEP = 1
FOOD_PER_LVL = 3

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BG_COLOR = (15, 20, 30)
GRID_COLOR = (25, 32, 45)
PANEL_COLOR = (10, 14, 22)

SNAKE_HEAD = (50, 220, 80)
SNAKE_BODY = (30, 160, 55)
SNAKE_OUT = (20, 100, 35)

FOOD_COLOR = (255, 70, 70)
FOOD_OUT = (180, 20, 20)

POISON_COLOR = (120, 0, 160)
POISON_OUT = (70, 0, 100)

WALL_COLOR = (80, 90, 110)
WALL_OUT = (50, 60, 80)

TEXT_COLOR = (200, 210, 230)
GOLD = (255, 210, 0)
LEVEL_COLOR = (100, 200, 255)
BLUE = (80, 160, 255)
RED = (255, 80, 80)

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("Arial", 42, bold=True)
font_med = pygame.font.SysFont("Arial", 26, bold=True)
font_small = pygame.font.SysFont("Arial", 18)


def cell_rect(col, row):
    return pygame.Rect(col * CELL, row * CELL + PANEL_H, CELL, CELL)


def draw_cell(surface, col, row, color, outline=None, radius=4):
    rect = cell_rect(col, row).inflate(-2, -2)
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if outline:
        pygame.draw.rect(surface, outline, rect, width=2, border_radius=radius)


def load_settings():
    try:
        with open("settings.json", "r") as file:
            return json.load(file)
    except:
        return {
            "snake_color": [50, 220, 80],
            "show_grid": True,
            "sound": False
        }


def draw_grid(surface, show_grid=True):
    field_rect = pygame.Rect(0, PANEL_H, SCREEN_W, SCREEN_H - PANEL_H)
    pygame.draw.rect(surface, BG_COLOR, field_rect)

    if show_grid:
        for r in range(ROWS + 1):
            y = r * CELL + PANEL_H
            pygame.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_W, y))

        for c in range(COLS + 1):
            x = c * CELL
            pygame.draw.line(surface, GRID_COLOR, (x, PANEL_H), (x, SCREEN_H))


def draw_hud(surface, score, level, food_eaten, fps, personal_best):
    pygame.draw.rect(surface, PANEL_COLOR, (0, 0, SCREEN_W, PANEL_H))
    pygame.draw.line(surface, WALL_COLOR, (0, PANEL_H), (SCREEN_W, PANEL_H), 2)

    score_text = font_med.render(f"Score: {score}", True, TEXT_COLOR)
    level_text = font_med.render(f"Level: {level}", True, LEVEL_COLOR)
    best_text = font_small.render(f"Best: {personal_best}", True, GOLD)
    speed_text = font_small.render(f"Speed: {fps}", True, TEXT_COLOR)

    surface.blit(score_text, (12, 8))
    surface.blit(level_text, (12, 34))
    surface.blit(best_text, (180, 10))
    surface.blit(speed_text, (SCREEN_W - 100, 12))

    progress = food_eaten % FOOD_PER_LVL
    progress_text = font_small.render(f"Next level: {progress}/{FOOD_PER_LVL}", True, TEXT_COLOR)
    surface.blit(progress_text, (SCREEN_W - 160, 34))


def show_overlay(surface, title, lines):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))

    title_text = font_big.render(title, True, WHITE)
    surface.blit(title_text, title_text.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 70)))

    for i, line in enumerate(lines):
        text = font_small.render(line, True, TEXT_COLOR)
        surface.blit(text, text.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + i * 28)))


def input_username():
    username = ""

    while True:
        screen.fill(BG_COLOR)

        title = font_med.render("Enter username:", True, WHITE)
        name_text = font_med.render(username + "|", True, GOLD)
        hint = font_small.render("Press ENTER to continue", True, TEXT_COLOR)

        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 50)))
        screen.blit(name_text, name_text.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))
        screen.blit(hint, hint.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 50)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username.strip()

                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]

                else:
                    if len(username) < 15 and event.unicode.isprintable():
                        username += event.unicode


def show_leaderboard():
    rows = get_top_10()

    while True:
        screen.fill(BG_COLOR)

        title = font_big.render("TOP 10", True, GOLD)
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 70)))

        y = 130

        if not rows:
            empty = font_small.render("No scores yet", True, WHITE)
            screen.blit(empty, empty.get_rect(center=(SCREEN_W // 2, y)))
        else:
            for i, row in enumerate(rows, start=1):
                username, score, level, played_at = row
                line = font_small.render(
                    f"{i}. {username} | Score: {score} | Level: {level}",
                    True,
                    WHITE
                )
                screen.blit(line, (50, y))
                y += 28

        back = font_small.render("ESC - Back", True, TEXT_COLOR)
        screen.blit(back, back.get_rect(center=(SCREEN_W // 2, SCREEN_H - 40)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return


def main_menu():
    while True:
        screen.fill(BG_COLOR)

        title = font_big.render("SNAKE", True, GOLD)
        screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 130)))

        screen.blit(font_med.render("1 - Play", True, WHITE), (170, 220))
        screen.blit(font_med.render("2 - Leaderboard", True, WHITE), (170, 270))
        screen.blit(font_med.render("3 - Quit", True, WHITE), (170, 320))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "play"
                elif event.key == pygame.K_2:
                    return "leaderboard"
                elif event.key == pygame.K_3:
                    pygame.quit()
                    sys.exit()


def random_free_pos(snake_body, walls, food=None, poison=None, bonus=None):
    occupied = set(snake_body) | set(walls)

    if food:
        occupied.add(food["pos"])
    if poison:
        occupied.add(poison["pos"])
    if bonus:
        occupied.add(bonus["pos"])

    while True:
        col = random.randint(1, COLS - 2)
        row = random.randint(1, ROWS - 2)

        if (col, row) not in occupied:
            return col, row


def generate_walls(level, snake):
    walls = set()

    if level < 3:
        return walls

    tries = 0

    while len(walls) < min(level * 2, 18) and tries < 200:
        col = random.randint(2, COLS - 3)
        row = random.randint(2, ROWS - 3)

        if (col, row) not in snake:
            walls.add((col, row))

        tries += 1

    return walls


def create_food(snake, walls, poison=None, bonus=None):
    return {
        "pos": random_free_pos(snake, walls, poison=poison, bonus=bonus),
        "weight": random.choice([1, 2, 3]),
        "timer": random.randint(80, 160)
    }


def create_poison(snake, walls, food=None, bonus=None):
    return {
        "pos": random_free_pos(snake, walls, food=food, bonus=bonus),
        "timer": random.randint(120, 220)
    }


def create_bonus(snake, walls, food=None, poison=None):
    return {
        "pos": random_free_pos(snake, walls, food=food, poison=poison),
        "kind": random.choice(["speed", "slow", "shield"]),
        "timer": random.randint(120, 220)
    }


def draw_food(food):
    pos = food["pos"]

    if food["weight"] == 1:
        color = FOOD_COLOR
    elif food["weight"] == 2:
        color = (255, 165, 0)
    else:
        color = GOLD

    rect = cell_rect(*pos).inflate(-4, -4)
    pygame.draw.ellipse(screen, color, rect)
    pygame.draw.ellipse(screen, FOOD_OUT, rect, 2)


def draw_poison(poison):
    rect = cell_rect(*poison["pos"]).inflate(-4, -4)
    pygame.draw.ellipse(screen, POISON_COLOR, rect)
    pygame.draw.ellipse(screen, POISON_OUT, rect, 2)


def draw_bonus(bonus):
    if bonus["kind"] == "speed":
        color = GOLD
        label = "+"
    elif bonus["kind"] == "slow":
        color = BLUE
        label = "-"
    else:
        color = RED
        label = "S"

    draw_cell(screen, *bonus["pos"], color, WHITE, radius=6)

    text = font_small.render(label, True, WHITE)
    screen.blit(text, text.get_rect(center=cell_rect(*bonus["pos"]).center))


def game_loop():
    settings = load_settings()

    snake_head_color = tuple(settings.get("snake_color", [50, 220, 80]))
    show_grid_setting = settings.get("show_grid", True)

    username = input_username()
    personal_best = get_personal_best(username)

    level = 1
    score = 0
    food_eaten = 0
    current_fps = FPS_START

    snake = [
        (COLS // 2, ROWS // 2),
        (COLS // 2 - 1, ROWS // 2),
        (COLS // 2 - 2, ROWS // 2)
    ]

    direction = (1, 0)
    next_dir = direction

    walls = generate_walls(level, snake)

    food = create_food(snake, walls)
    poison = create_poison(snake, walls, food=food)
    bonus = create_bonus(snake, walls, food=food, poison=poison)

    started = False
    game_over = False
    score_saved = False

    level_up_msg = 0

    speed_effect_timer = 0
    slow_effect_timer = 0
    shield_active = False

    while True:
        clock.tick(current_fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not started:
                        started = True
                    elif game_over:
                        return

                if event.key == pygame.K_l and game_over:
                    show_leaderboard()

                if not game_over:
                    if event.key == pygame.K_UP and direction != (0, 1):
                        next_dir = (0, -1)
                    elif event.key == pygame.K_DOWN and direction != (0, -1):
                        next_dir = (0, 1)
                    elif event.key == pygame.K_LEFT and direction != (1, 0):
                        next_dir = (-1, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                        next_dir = (1, 0)

        if not started:
            draw_grid(screen, show_grid_setting)
            draw_hud(screen, score, level, food_eaten, current_fps, personal_best)
            show_overlay(
                screen,
                "SNAKE",
                [
                    f"Player: {username}",
                    "Arrow keys - move",
                    "SPACE - start"
                ]
            )
            pygame.display.flip()
            continue

        if game_over:
            if not score_saved:
                save_result(username, score, level)
                score_saved = True

            draw_grid(screen, show_grid_setting)

            for w in walls:
                draw_cell(screen, *w, WALL_COLOR, WALL_OUT, radius=2)

            draw_food(food)
            draw_poison(poison)
            draw_bonus(bonus)

            for i, seg in enumerate(snake):
                color = snake_head_color if i == 0 else SNAKE_BODY
                draw_cell(screen, *seg, color, SNAKE_OUT)

            draw_hud(screen, score, level, food_eaten, current_fps, personal_best)

            show_overlay(
                screen,
                "GAME OVER",
                [
                    f"Score: {score} | Level: {level}",
                    "SPACE - menu",
                    "L - leaderboard"
                ]
            )

            pygame.display.flip()
            continue

        if speed_effect_timer > 0:
            speed_effect_timer -= 1
            current_fps = FPS_START + (level - 1) * FPS_STEP + 3
        elif slow_effect_timer > 0:
            slow_effect_timer -= 1
            current_fps = max(3, FPS_START + (level - 1) * FPS_STEP - 3)
        else:
            current_fps = FPS_START + (level - 1) * FPS_STEP

        direction = next_dir
        head_c, head_r = snake[0]
        new_head = (head_c + direction[0], head_r + direction[1])

        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            if shield_active:
                shield_active = False
                new_head = snake[0]
            else:
                game_over = True
                continue

        if new_head in snake[1:]:
            if shield_active:
                shield_active = False
                new_head = snake[0]
            else:
                game_over = True
                continue

        if new_head in walls:
            game_over = True
            continue

        if new_head == food["pos"]:
            snake.insert(0, new_head)

            score += 10 * level * food["weight"]
            food_eaten += 1

            if food_eaten % FOOD_PER_LVL == 0:
                level += 1
                level_up_msg = current_fps * 2
                walls = generate_walls(level, snake)

            food = create_food(snake, walls, poison=poison, bonus=bonus)

        elif new_head == poison["pos"]:
            snake.insert(0, new_head)

            for _ in range(2):
                if len(snake) > 1:
                    snake.pop()

            if len(snake) <= 1:
                game_over = True
                continue

            poison = create_poison(snake, walls, food=food, bonus=bonus)

        elif new_head == bonus["pos"]:
            snake.insert(0, new_head)
            snake.pop()

            if bonus["kind"] == "speed":
                speed_effect_timer = current_fps * 5

            elif bonus["kind"] == "slow":
                slow_effect_timer = current_fps * 5

            elif bonus["kind"] == "shield":
                shield_active = True

            bonus = create_bonus(snake, walls, food=food, poison=poison)

        else:
            snake.insert(0, new_head)
            snake.pop()

            food["timer"] -= 1
            poison["timer"] -= 1
            bonus["timer"] -= 1

            if food["timer"] <= 0:
                food = create_food(snake, walls, poison=poison, bonus=bonus)

            if poison["timer"] <= 0:
                poison = create_poison(snake, walls, food=food, bonus=bonus)

            if bonus["timer"] <= 0:
                bonus = create_bonus(snake, walls, food=food, poison=poison)

        if level_up_msg > 0:
            level_up_msg -= 1

        draw_grid(screen, show_grid_setting)

        for w in walls:
            draw_cell(screen, *w, WALL_COLOR, WALL_OUT, radius=2)

        draw_food(food)
        draw_poison(poison)
        draw_bonus(bonus)

        for i, seg in enumerate(snake):
            color = snake_head_color if i == 0 else SNAKE_BODY
            draw_cell(screen, *seg, color, SNAKE_OUT)

        draw_hud(screen, score, level, food_eaten, current_fps, personal_best)

        if shield_active:
            shield_text = font_small.render("Shield active", True, GOLD)
            screen.blit(shield_text, (SCREEN_W // 2 - 50, 8))

        if level_up_msg > 0:
            msg = font_med.render(f"LEVEL {level}!", True, GOLD)
            screen.blit(msg, msg.get_rect(center=(SCREEN_W // 2, PANEL_H + 40)))

        pygame.display.flip()