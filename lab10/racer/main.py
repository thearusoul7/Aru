import pygame
import random
import sys

pygame.init()


#  Константы
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600

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

# Частота кадров
FPS = 60


#  Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer 🏎️")
clock = pygame.time.Clock()


#  Шрифты
font_large  = pygame.font.SysFont("Arial", 48, bold=True)
font_medium = pygame.font.SysFont("Arial", 28, bold=True)
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
        self.angle  = 0   # угол для анимации «блеска»

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
        pygame.draw.circle(surface, YELLOW, (cx, cy), r)
        # Тёмный ободок
        pygame.draw.circle(surface, ORANGE, (cx, cy), r, 2)
        # Символ $
        sym = font_small.render("$", True, ORANGE)
        surface.blit(sym, sym.get_rect(center=(cx, cy)))


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


def draw_hud(surface, score, coins, level):
    """Рисует интерфейс: счёт, уровень и счётчик монет."""
    # Очки — верхний левый угол
    score_surf = font_small.render(f"Score: {score}", True, WHITE)
    surface.blit(score_surf, (10, 10))

    # Уровень — под очками
    level_surf = font_small.render(f"Level: {level}", True, WHITE)
    surface.blit(level_surf, (10, 35))

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

#  ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ

def game_loop():
    """Основная функция игры."""

    # Состояние игры
    player      = PlayerCar()
    enemies     = []
    coins_list  = []
    road_lines  = []

    score       = 0     # набранные очки (за время выживания)
    coins_count = 0     # подобранные монеты
    level       = 1     # текущий уровень

    base_speed      = 4         # начальная скорость объектов
    speed           = base_speed
    enemy_spawn_cd  = 90        # кадров до следующего врага
    coin_spawn_cd   = random.randint(120, 240)  # кадров до следующей монеты
    line_spawn_cd   = 30        # кадров до следующей разметки

    frame           = 0         # счётчик кадров

    # Создаём начальную разметку по центру дороги
    center_x = ROAD_LEFT + ROAD_WIDTH // 2
    for y in range(0, SCREEN_HEIGHT, 80):
        road_lines.append(RoadLine(center_x, y, speed))

    running    = True
    game_over  = False
    started    = False          # показываем стартовый экран

    while running:
        clock.tick(FPS)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not started:
                        started = True          # запуск игры
                    elif game_over:
                        game_loop()             # рестарт
                        return

        # Стартовый экран
        if not started:
            draw_background(screen)
            show_message(screen, "RACER", "Press SPACE to start")
            pygame.display.flip()
            continue

        # Экран Game Over
        if game_over:
            draw_background(screen)
            for line in road_lines:
                line.draw(screen)
            for e in enemies:
                e.draw(screen)
            player.draw(screen)
            draw_hud(screen, score, coins_count, level)
            show_message(screen, "GAME OVER",
                         f"Score: {score}  Coins: {coins_count}  |  SPACE to restart")
            pygame.display.flip()
            continue

        frame += 1
        score += 1   # очки растут с каждым кадром выживания

        # Уровни: каждые 500 очков скорость растёт
        new_level = score // 500 + 1
        if new_level != level:
            level = new_level
            speed = base_speed + (level - 1) * 0.8   # +0.8 пикселя за уровень

        # Ввод игрока
        keys = pygame.key.get_pressed()
        player.move(keys)

        # Спавн разметки дороги
        line_spawn_cd -= 1
        if line_spawn_cd <= 0:
            road_lines.append(RoadLine(center_x, -RoadLine.HEIGHT, speed))
            line_spawn_cd = 30

        # Спавн вражеских машин
        enemy_spawn_cd -= 1
        if enemy_spawn_cd <= 0:
            enemies.append(EnemyCar(speed))
            # С уровнем машины появляются чаще
            enemy_spawn_cd = max(35, 90 - level * 8)

        # Спавн монет
        coin_spawn_cd -= 1
        if coin_spawn_cd <= 0:
            coins_list.append(Coin(speed))
            coin_spawn_cd = random.randint(100, 220)   # случайный интервал

        # Обновление объектов
        for line in road_lines:
            line.update()
        for enemy in enemies:
            enemy.update()
        for coin in coins_list:
            coin.update()

        # Удаление объектов за нижним краем
        road_lines = [l for l in road_lines  if not l.is_offscreen()]
        enemies    = [e for e in enemies     if not e.is_offscreen()]
        coins_list = [c for c in coins_list  if not c.is_offscreen()]

        # Проверка столкновений
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                game_over = True
                break

        # Подбор монет
        collected = []
        for coin in coins_list:
            if player.rect.colliderect(coin.rect):
                coins_count += 1
                score       += 50    # бонус за монету
                collected.append(coin)
        for c in collected:
            coins_list.remove(c)

        # Отрисовка
        draw_background(screen)

        for line in road_lines:
            line.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for coin in coins_list:
            coin.draw(screen)

        player.draw(screen)
        draw_hud(screen, score, coins_count, level)

        pygame.display.flip()


if __name__ == "__main__":
    game_loop()