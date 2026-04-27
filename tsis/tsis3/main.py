import pygame
import random
import sys
import json

from persistence import save_score
from persistence import save_score, load_leaderboard

def load_leaderboard():
    try:
        with open("leaderboard.json", "r") as file:
            return json.load(file)
    except:
        return []


def save_score(username, score, coins, distance):
    leaderboard = load_leaderboard()

    leaderboard.append({
        "score": score,
        "coins": coins,
        "distance": int(distance)
    })

    leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)
    leaderboard = leaderboard[:10]

    with open("leaderboard.json", "w") as file:
        json.dump(leaderboard, file, indent=4)

pygame.init()


#  Константы
SCREEN_WIDTH  = 410
SCREEN_HEIGHT = 610

# Цвета (R, G, B)
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
RED        = (255,  50,  50)
BLUE       = (50,  100, 255)
YELLOW     = (255, 220,   0)
GRAY       = (80,   80,  80)
DARK_GRAY  = (50,   50,  50)
GREEN      = (0,  200,   0)
ORANGE     = (255, 165,   0)

# Параметры дороги
ROAD_LEFT   = 60
ROAD_RIGHT  = 340
ROAD_WIDTH  = ROAD_RIGHT - ROAD_LEFT

#уровень
difficulty = "Easy"

# Частота кадров
FPS = 60


#  Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer 🏎️")
clock = pygame.time.Clock()


#  Шрифты
font_large  = pygame.font.SysFont("Arial", 48, bold=True)
font_medium = pygame.font.SysFont("Arial", 20, bold=True)
font_small  = pygame.font.SysFont("Arial", 22)


#  КЛАССЫ

class PlayerCar:
    """Машина игрока — управляется клавишами влево/вправо."""

    WIDTH  = 40
    HEIGHT = 70
    SPEED  = 5

    def __init__(self):
        # Стартовая позиция — по центру дороги, внизу экрана
        self.x = SCREEN_WIDTH // 2 - self.WIDTH // 2
        self.y = SCREEN_HEIGHT - self.HEIGHT - 20
        self.rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
        self.slow_timer = 0
        self.base_speed = 5
        self.shield = False
        self.nitro_timer = 0
        self.active_power = None

    def move(self, keys):
        """Двигает машину по нажатым клавишам, не выходя за границы дороги."""
        if keys[pygame.K_LEFT]  and self.rect.left  > ROAD_LEFT  + 5:
            self.rect.x -= self.SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < ROAD_RIGHT - 5:
            self.rect.x += self.SPEED

    def draw(self, surface):
        """Рисует машину игрока (синяя)."""
        r = self.rect
        # Кузов
        pygame.draw.rect(surface, BLUE, r, border_radius=6)
        # Лобовое стекло
        pygame.draw.rect(surface, (180, 220, 255),
                         (r.x + 5, r.y + 8, r.width - 10, 18), border_radius=3)
        # Заднее стекло
        pygame.draw.rect(surface, (180, 220, 255),
                         (r.x + 5, r.y + r.height - 26, r.width - 10, 14), border_radius=3)
        # Колёса
        wheel_color = DARK_GRAY
        pygame.draw.rect(surface, wheel_color, (r.x - 6,          r.y + 8,  8, 18), border_radius=3)
        pygame.draw.rect(surface, wheel_color, (r.x + r.width - 2, r.y + 8,  8, 18), border_radius=3)
        pygame.draw.rect(surface, wheel_color, (r.x - 6,          r.y + r.height - 26, 8, 18), border_radius=3)
        pygame.draw.rect(surface, wheel_color, (r.x + r.width - 2, r.y + r.height - 26, 8, 18), border_radius=3)


class EnemyCar:
    """Машина-препятствие — едет сверху вниз."""

    WIDTH  = 40
    HEIGHT = 70

    COLORS = [
        (220,  50,  50),   # красный
        (50,  180,  50),   # зелёный
        (200, 100, 200),   # фиолетовый
        (255, 140,   0),   # оранжевый
    ]

    def __init__(self, speed):
        # Случайная полоса: левая, центральная или правая
        lane_x = [
            ROAD_LEFT + 10,
            ROAD_LEFT + ROAD_WIDTH // 2 - self.WIDTH // 2,
            ROAD_RIGHT - self.WIDTH - 10,
        ]
        self.rect  = pygame.Rect(random.choice(lane_x), -self.HEIGHT,
                                 self.WIDTH, self.HEIGHT)
        self.speed = speed
        self.color = random.choice(self.COLORS)

    def update(self):
        """Двигает машину вниз."""
        self.rect.y += self.speed

    def is_offscreen(self):
        """Проверяет, вышла ли машина за нижний край экрана."""
        return self.rect.top > SCREEN_HEIGHT

    def draw(self, surface):
        """Рисует машину-препятствие."""
        r = self.rect
        pygame.draw.rect(surface, self.color, r, border_radius=6)
        # Лобовое стекло (снизу, т.к. едет к нам)
        pygame.draw.rect(surface, (255, 255, 200),
                         (r.x + 5, r.y + r.height - 26, r.width - 10, 14), border_radius=3)
        # Фары
        pygame.draw.circle(surface, YELLOW, (r.x + 8,          r.y + r.height - 10), 5)
        pygame.draw.circle(surface, YELLOW, (r.x + r.width - 8, r.y + r.height - 10), 5)
        # Колёса
        pygame.draw.rect(surface, DARK_GRAY, (r.x - 6,           r.y + 8,  8, 18), border_radius=3)
        pygame.draw.rect(surface, DARK_GRAY, (r.x + r.width - 2, r.y + 8,  8, 18), border_radius=3)
        pygame.draw.rect(surface, DARK_GRAY, (r.x - 6,           r.y + r.height - 26, 8, 18), border_radius=3)
        pygame.draw.rect(surface, DARK_GRAY, (r.x + r.width - 2, r.y + r.height - 26, 8, 18), border_radius=3)


class Coin:
    """Монета — случайно появляется на дороге, даёт очки при подборе."""

    RADIUS = 12

    def __init__(self, speed):
        # Случайная позиция по X внутри дороги
        self.x = random.randint(ROAD_LEFT + self.RADIUS + 10,
                                ROAD_RIGHT - self.RADIUS - 10)
        self.y = -self.RADIUS
        self.speed  = speed
        self.rect   = pygame.Rect(self.x - self.RADIUS, self.y - self.RADIUS,
                                  self.RADIUS * 2, self.RADIUS * 2)
        # weight of coin (gives more score)
        self.weight = random.choice([1, 2, 3])
        self.angle  = 0 # угол для анимации «блеска»
        
    def update(self):
        """Двигает монету вниз и обновляет хитбокс."""
        self.y += self.speed
        self.rect.center = (self.x, int(self.y))
        self.angle = (self.angle + 4) % 360   # анимация вращения

    def is_offscreen(self):
        return self.y - self.RADIUS > SCREEN_HEIGHT

    def draw(self, surface):
        """Рисует монету с простой анимацией блеска."""
        cx, cy = self.x, int(self.y)
        r = self.RADIUS
        # Основной круг
       # цвет зависит от веса монеты
        if self.weight == 1:
            color = YELLOW
        elif self.weight == 2:
            color = ORANGE
        else:
            color = GREEN

        pygame.draw.circle(surface, color, (cx, cy), r)
        
        # Тёмный ободок
        pygame.draw.circle(surface, ORANGE, (cx, cy), r, 2)
        # Символ $
        sym = font_small.render("$", True, ORANGE)
        surface.blit(sym, sym.get_rect(center=(cx, cy)))

class Obstacle:
    WIDTH = 45
    HEIGHT = 35

    def __init__(self, speed):
        lane_x = [
            ROAD_LEFT + 10,
            ROAD_LEFT + ROAD_WIDTH // 2 - self.WIDTH // 2,
            ROAD_RIGHT - self.WIDTH - 10,
        ]

        self.rect = pygame.Rect(
            random.choice(lane_x),
            -self.HEIGHT,
            self.WIDTH,
            self.HEIGHT
        )

        self.speed = speed
        self.kind = random.choice(["oil", "barrier"])

    def update(self):
        self.rect.y += self.speed

    def is_offscreen(self):
        return self.rect.top > SCREEN_HEIGHT

    def draw(self, surface):
        if self.kind == "oil":
            pygame.draw.ellipse(surface, BLACK, self.rect)
        else:
            pygame.draw.rect(surface, ORANGE, self.rect, border_radius=5)
            pygame.draw.line(surface, WHITE, self.rect.topleft, self.rect.bottomright, 3)
            pygame.draw.line(surface, WHITE, self.rect.topright, self.rect.bottomleft, 3)


class PowerUp:
    WIDTH = 32
    HEIGHT = 32

    def __init__(self, speed):
        lane_x = [
            ROAD_LEFT + 15,
            ROAD_LEFT + ROAD_WIDTH // 2 - self.WIDTH // 2,
            ROAD_RIGHT - self.WIDTH - 15,
        ]

        self.rect = pygame.Rect(
            random.choice(lane_x),
            -self.HEIGHT,
            self.WIDTH,
            self.HEIGHT
        )

        self.speed = speed
        self.kind = random.choice(["nitro", "shield", "repair"])

    def update(self):
        self.rect.y += self.speed

    def is_offscreen(self):
        return self.rect.top > SCREEN_HEIGHT

    def draw(self, surface):
        if self.kind == "nitro":
            color = YELLOW
            text = "N"
        elif self.kind == "shield":
            color = BLUE
            text = "S"
        else:
            color = GREEN
            text = "R"

        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        label = font_small.render(text, True, WHITE)
        surface.blit(label, label.get_rect(center=self.rect.center))


class RoadLine:
    """Белая разметка дороги — движется вниз для эффекта скорости."""

    WIDTH  = 10
    HEIGHT = 40

    def __init__(self, x, y, speed):
        self.rect  = pygame.Rect(x - self.WIDTH // 2, y, self.WIDTH, self.HEIGHT)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

    def is_offscreen(self):
        return self.rect.top > SCREEN_HEIGHT

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=3)

#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ

def draw_background(surface):
    """Рисует фон: небо, обочины и полотно дороги."""
    surface.fill((34, 139, 34))            # зелёная трава по бокам
    # Дорога
    pygame.draw.rect(surface, GRAY,
                     (ROAD_LEFT, 0, ROAD_WIDTH, SCREEN_HEIGHT))
    # Белые бордюры
    pygame.draw.line(surface, WHITE, (ROAD_LEFT,  0), (ROAD_LEFT,  SCREEN_HEIGHT), 3)
    pygame.draw.line(surface, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, SCREEN_HEIGHT), 3)


def draw_hud(surface, score, coins, level, distance):  
    """Рисует интерфейс: счёт, уровень и счётчик монет."""
    # Очки — верхний левый угол
    score_surf = font_small.render(f"Score: {score}", True, WHITE)
    surface.blit(score_surf, (10, 10))

    # Уровень — под очками
    level_surf = font_small.render(f"Level: {level}", True, WHITE)
    surface.blit(level_surf, (10, 35))
    distance_surf = font_small.render(f"Distance: {int(distance)} m", True, WHITE)
    surface.blit(distance_surf, (10, 60))

    # Монеты — верхний правый угол
    coin_text = font_medium.render(f"🪙 {coins}", True, YELLOW)
    surface.blit(coin_text, (SCREEN_WIDTH - coin_text.get_width() - 10, 8))


def show_message(surface, title, subtitle):
    """Отображает экран с сообщением (старт / конец игры)."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    t1 = font_large.render(title, True, WHITE)
    t2 = font_small.render(subtitle, True, (200, 200, 200))
    surface.blit(t1, t1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)))
    surface.blit(t2, t2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)))

def can_spawn_at(x, existing_objects, min_y_gap=120):
    new_rect = pygame.Rect(x, -80, 45, 80)

    for obj in existing_objects:
        if abs(obj.rect.x - x) < 50 and obj.rect.y < min_y_gap:
            return False

    return True

#топ-10 на экране
def show_leaderboard(surface):
    leaderboard = load_leaderboard()

    title = font_medium.render("TOP 10", True, YELLOW)
    surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 120)))

    y = 170

    if not leaderboard:
        empty = font_small.render("No scores yet", True, WHITE)
        surface.blit(empty, empty.get_rect(center=(SCREEN_WIDTH // 2, y)))
        return

    for i, item in enumerate(leaderboard, start=1):
        line = font_small.render(
             f"{i}. {item.get('name', 'Player')} | Score: {item['score']} | Dist: {item['distance']}m",
             True,
             WHITE
)
        surface.blit(line, (30, y))
        y += 30


difficulty = "Easy"

def settings_screen():
    global difficulty

    while True:
        draw_background(screen)

        title = font_medium.render("SETTINGS", True, YELLOW)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 160)))

        diff_text = font_small.render(f"Difficulty: {difficulty}  (press D)", True, WHITE)
        screen.blit(diff_text, (70, 260))

        back_text = font_small.render("ESC - Back to menu", True, WHITE)
        screen.blit(back_text, (70, 320))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                if event.key == pygame.K_d:
                    if difficulty == "Easy":
                        difficulty = "Medium"
                    elif difficulty == "Medium":
                        difficulty = "Hard"
                    else:
                        difficulty = "Easy"

def main_menu():
    while True:
        draw_background(screen)

        title = font_large.render("RACER", True, YELLOW)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 150)))

        screen.blit(font_small.render("1 - Play", True, WHITE), (120, 240))
        screen.blit(font_small.render("2 - Leaderboard", True, WHITE), (120, 280))
        screen.blit(font_small.render("3 - Settings", True, WHITE), (120, 320))
        screen.blit(font_small.render("4 - Quit", True, WHITE), (120, 360))

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
                    return "settings"
                elif event.key == pygame.K_4:
                    pygame.quit()
                    sys.exit()

#
def get_base_speed():
    if difficulty == "Easy":
        return 3
    elif difficulty == "Medium":
        return 4
    else:
        return 6

#  ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ

def game_loop():
    """Основная функция игры."""

    # Состояние игры
    player      = PlayerCar()
    enemies     = []
    coins_list  = []
    road_lines  = []
    obstacles   = []
    powerups    = []

    score       = 0     # набранные очки (за время выживания)
    coins_count = 0     # подобранные монеты
    level       = 1     # текущий уровень
    distance    = 0

    base_speed      = get_base_speed()         # начальная скорость объектов
    speed           = base_speed
    enemy_spawn_cd  = 90        # кадров до следующего врага
    coin_spawn_cd   = random.randint(120, 240)  # кадров до следующей монеты
    powerup_spawn_cd = random.randint(200, 350)
    obstacle_spawn_cd = random.randint(180, 300)
    line_spawn_cd   = 30        # кадров до следующей разметки

    frame           = 0         # счётчик кадров

    # Создаём начальную разметку по центру дороги
    center_x = ROAD_LEFT + ROAD_WIDTH // 2
    for y in range(0, SCREEN_HEIGHT, 80):
        road_lines.append(RoadLine(center_x, y, speed))

    running    = True
    game_over  = False
    started    = False          # показываем стартовый экран
    score_saved = False
    username = ""
    entering_name = True

    while running:
        clock.tick(FPS)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if entering_name:
                    if event.key == pygame.K_RETURN and username.strip() != "":
                        entering_name = False
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    else:
                        if len(username) < 12:
                             username += event.unicode
                    continue
                if event.key == pygame.K_SPACE:
                    if not started:
                        started = True          # запуск игры
                    elif game_over:
                        game_loop()             # рестарт
                        return
        if entering_name:
            draw_background(screen)
            show_message(screen, "ENTER NAME", username + "|")
            pygame.display.flip()
            continue

        # Стартовый экран
        if not started:
            draw_background(screen)
            show_message(screen, "RACER", "Press SPACE to start")
            pygame.display.flip()
            continue

        # Экран Game Over
        if game_over:
            if not score_saved:
                save_score(username, score, coins_count, distance)
                score_saved = True
            draw_background(screen)
            for line in road_lines:
                line.draw(screen)
            for e in enemies:
                e.draw(screen)
            for obstacle in obstacles:
                obstacle.draw(screen)
            player.draw(screen)
            draw_hud(screen, score, coins_count, level, distance)
            #show_message(screen, "GAME OVER",
                         #f"Score: {score}  Coins: {coins_count}  |  SPACE to restart")
            show_leaderboard(screen)
            pygame.display.flip()
            continue

        frame += 1
        score += 1   # очки растут с каждым кадром выживания
        distance += speed / 10

        # Уровни: каждые 500 очков скорость растёт
        new_level = score // 500 + 1
        if new_level != level:
            level = new_level
            speed = base_speed + (level - 1) * 0.8   # +0.8 пикселя за уровень

        # Ввод игрока
        keys = pygame.key.get_pressed()
        player.move(keys)

        # масло
        if player.slow_timer > 0:
            player.SPEED = 1
            player.slow_timer -= 1
        else:
            player.SPEED = player.base_speed

        # нитро
        if player.nitro_timer > 0:
            player.SPEED = 8
            player.nitro_timer -= 1

        if player.slow_timer > 0:
            player.SPEED = 1   # очень медленно
            player.slow_timer -= 1
        else:
            player.SPEED = player.base_speed

        # Спавн разметки дороги
        line_spawn_cd -= 1
        if line_spawn_cd <= 0:
            road_lines.append(RoadLine(center_x, -RoadLine.HEIGHT, speed))
            line_spawn_cd = 30

        # Спавн вражеских машин
        enemy_spawn_cd -= 1
        if enemy_spawn_cd <= 0:
            new_enemy = EnemyCar(speed)
            all_objects = enemies + coins_list + obstacles + powerups

            if can_spawn_at(new_enemy.rect.x, all_objects):
                enemies.append(new_enemy)
            # С уровнем машины появляются чаще
            enemy_spawn_cd = max(35, 90 - level * 8)

        # Спавн монет
        coin_spawn_cd -= 1
        if coin_spawn_cd <= 0:
            new_coin = Coin(speed)
            all_objects = enemies + coins_list + obstacles + powerups

            if can_spawn_at(new_coin.rect.x, all_objects):
                coins_list.append(new_coin)
            coin_spawn_cd = random.randint(100, 220)   # случайный интервал

        powerup_spawn_cd -= 1
        if powerup_spawn_cd <= 0:
            new_powerup = PowerUp(speed)
            all_objects = enemies + coins_list + obstacles + powerups

            if can_spawn_at(new_powerup.rect.x, all_objects):
                powerups.append(new_powerup)
            powerup_spawn_cd = random.randint(200, 350)

        obstacle_spawn_cd -= 1
        if obstacle_spawn_cd <= 0:
            new_obstacle = Obstacle(speed)
            all_objects = enemies + coins_list + obstacles + powerups

            if can_spawn_at(new_obstacle.rect.x, all_objects):
                obstacles.append(new_obstacle)
            obstacle_spawn_cd = random.randint(180, 300)

        # Обновление объектов
        for line in road_lines:
            line.update()
        for enemy in enemies:
            enemy.speed = speed   # обновляем скорость
            enemy.update()
        for coin in coins_list:
            coin.update()
        for obstacle in obstacles:
            obstacle.speed = speed
            obstacle.update()
        for p in powerups:
            p.speed = speed
            p.update()

        # Удаление объектов за нижним краем
        road_lines = [l for l in road_lines  if not l.is_offscreen()]
        enemies    = [e for e in enemies     if not e.is_offscreen()]
        coins_list = [c for c in coins_list  if not c.is_offscreen()]
        obstacles = [o for o in obstacles if not o.is_offscreen()]
        powerups = [p for p in powerups if not p.is_offscreen()]

        # Проверка столкновений
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                if player.shield:
                    player.shield = False
                    enemies.remove(enemy)
                else:
                    game_over = True
                    break

        #спавн препятствий
        for obstacle in obstacles:
            if player.rect.colliderect(obstacle.rect):
                if obstacle.kind == "barrier":
                    game_over = True
                    break
                elif obstacle.kind == "oil":
                    player.slow_timer = 300
                    obstacles.remove(obstacle)
                    break

        # Подбор монет
        collected = []
        for coin in coins_list:
            if player.rect.colliderect(coin.rect):
                coins_count += coin.weight
                score += 50 * coin.weight   # больше вес → больше очков    # бонус за монету
                collected.append(coin)
                # increase enemy speed every 5 coins
                if coins_count % 5 == 0:
                    speed += 1
        for c in collected:
            coins_list.remove(c)


        for p in powerups:
            if player.rect.colliderect(p.rect):

               if p.kind == "shield":
                   player.shield = True

               elif p.kind == "nitro":
                   player.nitro_timer = 180   # 3 секунды

               elif p.kind == "repair":
                   player.slow_timer = 0

               powerups.remove(p)
               break

        # Отрисовка
        draw_background(screen)

        for line in road_lines:
            line.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for coin in coins_list:
            coin.draw(screen)
        for obstacle in obstacles:
            obstacle.draw(screen)
        for p in powerups:
            p.draw(screen)

        player.draw(screen)
        draw_hud(screen, score, coins_count, level, distance)

        pygame.display.flip()


if __name__ == "__main__":
    while True:
        choice = main_menu()

        if choice == "play":
            game_loop()

        elif choice == "leaderboard":
            while True:
                draw_background(screen)
                show_leaderboard(screen)

                back = font_small.render("Press any key to return", True, WHITE)
                screen.blit(back, back.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)))

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    if event.type == pygame.KEYDOWN:
                        break
                else:
                    continue

                break

        elif choice == "settings":
            settings_screen()