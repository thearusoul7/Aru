import pygame
import sys
import datetime

from tools import canvas_pos, flood_fill, draw_preview, commit_shape


pygame.init()

SCREEN_W = 900
SCREEN_H = 780
TOOLBAR_W = 160

CANVAS_X = TOOLBAR_W
CANVAS_W = SCREEN_W - TOOLBAR_W
CANVAS_H = SCREEN_H

BG_CANVAS = (255, 255, 255)
BG_PANEL = (30, 35, 45)
HIGHLIGHT = (90, 140, 220)
TEXT_COLOR = (210, 215, 230)
DIVIDER = (55, 62, 78)

ERASER_SIZE = 24

TOOLS = [
    "Pencil", "Line", "Rectangle", "Circle", "Square",
    "Right Triangle", "Equilateral Triangle", "Rhombus",
    "Eraser", "Fill", "Text"
]

PALETTE = [
    (0, 0, 0), (80, 80, 80), (160, 160, 160), (255, 255, 255),
    (255, 0, 0), (180, 0, 0), (255, 100, 0), (200, 60, 0),
    (255, 200, 0), (180, 140, 0), (0, 200, 0), (0, 120, 0),
    (0, 200, 200), (0, 100, 160), (0, 0, 255), (0, 0, 140),
    (180, 0, 180), (100, 0, 120), (255, 150, 200), (150, 80, 40),
]

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

font_tool = pygame.font.SysFont("Arial", 16, bold=True)
font_label = pygame.font.SysFont("Arial", 13)
font_text = pygame.font.SysFont("Arial", 28)

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(BG_CANVAS)


def draw_toolbar(surface, active_tool, draw_color, brush_size):
    pygame.draw.rect(surface, BG_PANEL, (0, 0, TOOLBAR_W, SCREEN_H))
    pygame.draw.line(surface, DIVIDER, (TOOLBAR_W - 1, 0), (TOOLBAR_W - 1, SCREEN_H), 2)

    y = 12

    title = font_tool.render("Paint", True, HIGHLIGHT)
    surface.blit(title, (10, y))
    y += 30

    pygame.draw.line(surface, DIVIDER, (8, y), (TOOLBAR_W - 8, y))
    y += 10

    icons = {
        "Pencil": "P",
        "Line": "/",
        "Rectangle": "Rect",
        "Circle": "O",
        "Square": "Sq",
        "Right Triangle": "RT",
        "Equilateral Triangle": "ET",
        "Rhombus": "Rh",
        "Eraser": "E",
        "Fill": "F",
        "Text": "T"
    }

    for tool in TOOLS:
        btn_rect = pygame.Rect(8, y, TOOLBAR_W - 16, 30)

        if tool == active_tool:
            pygame.draw.rect(surface, HIGHLIGHT, btn_rect, border_radius=6)
        else:
            pygame.draw.rect(surface, (50, 58, 75), btn_rect, border_radius=6)

        label = font_label.render(f"{icons[tool]}  {tool}", True, TEXT_COLOR)
        surface.blit(label, (btn_rect.x + 8, btn_rect.y + 7))
        y += 36

    y += 6
    pygame.draw.line(surface, DIVIDER, (8, y), (TOOLBAR_W - 8, y))
    y += 10

    sz_label = font_label.render(f"Size: {brush_size}px", True, TEXT_COLOR)
    surface.blit(sz_label, (10, y))
    y += 20

    hint = font_label.render("1=2px  2=5px  3=10px", True, (120, 130, 150))
    surface.blit(hint, (10, y))
    y += 24

    pygame.draw.line(surface, DIVIDER, (8, y), (TOOLBAR_W - 8, y))
    y += 10

    pal_label = font_label.render("Colors:", True, TEXT_COLOR)
    surface.blit(pal_label, (10, y))
    y += 18

    cell_size = 28
    cols = 4

    for i, color in enumerate(PALETTE):
        col = i % cols
        row = i // cols

        cx = 10 + col * (cell_size + 3)
        cy = y + row * (cell_size + 3)

        r = pygame.Rect(cx, cy, cell_size, cell_size)
        pygame.draw.rect(surface, color, r, border_radius=4)

        if color == draw_color:
            pygame.draw.rect(surface, (255, 255, 255), r, 2, border_radius=4)

    y += ((len(PALETTE) - 1) // cols + 1) * (cell_size + 3) + 8

    cur_label = font_label.render("Current:", True, TEXT_COLOR)
    surface.blit(cur_label, (10, y))
    y += 18

    pygame.draw.rect(surface, draw_color, (10, y, 50, 26), border_radius=5)
    pygame.draw.rect(surface, (200, 200, 200), (10, y, 50, 26), 2, border_radius=5)

    clr = font_label.render("C Clear | Ctrl+S Save", True, (160, 100, 100))
    surface.blit(clr, (10, SCREEN_H - 24))


def get_tool_at(mx, my):
    y = 62

    for tool in TOOLS:
        btn_rect = pygame.Rect(8, y, TOOLBAR_W - 16, 30)

        if btn_rect.collidepoint(mx, my):
            return tool

        y += 36

    return None


def get_palette_color(mx, my):
    y_start = 62 + len(TOOLS) * 36 + 80
    cell_size = 28
    cols = 4

    for i, color in enumerate(PALETTE):
        col = i % cols
        row = i // cols

        cx = 10 + col * (cell_size + 3)
        cy = y_start + row * (cell_size + 3)

        r = pygame.Rect(cx, cy, cell_size, cell_size)

        if r.collidepoint(mx, my):
            return color

    return None


def main():
    active_tool = "Pencil"
    draw_color = (0, 0, 0)
    brush_size = 5

    drawing = False
    start_pos = None
    prev_pos = None

    typing = False
    text = ""
    text_pos = None

    while True:
        clock.tick(60)

        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if typing and active_tool == "Text":
                    if event.key == pygame.K_RETURN:
                        text_surface = font_text.render(text, True, draw_color)
                        canvas.blit(text_surface, text_pos)

                        typing = False
                        text = ""
                        text_pos = None

                    elif event.key == pygame.K_ESCAPE:
                        typing = False
                        text = ""
                        text_pos = None

                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]

                    else:
                        text += event.unicode

                else:
                    if event.key == pygame.K_1:
                        brush_size = 2

                    elif event.key == pygame.K_2:
                        brush_size = 5

                    elif event.key == pygame.K_3:
                        brush_size = 10

                    elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                        brush_size = min(brush_size + 1, 30)

                    elif event.key == pygame.K_MINUS:
                        brush_size = max(brush_size - 1, 1)

                    elif event.key == pygame.K_c:
                        canvas.fill(BG_CANVAS)

                    elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        filename = f"canvas_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        pygame.image.save(canvas, filename)
                        print(f"Saved: {filename}")

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                if mx < TOOLBAR_W:
                    tool = get_tool_at(mx, my)

                    if tool:
                        active_tool = tool
                        typing = False
                        text = ""
                        text_pos = None

                    color = get_palette_color(mx, my)

                    if color:
                        draw_color = color

                else:
                    cx, cy = canvas_pos(mx, my, CANVAS_X)

                    if active_tool == "Fill":
                        flood_fill(canvas, cx, cy, draw_color, CANVAS_W, CANVAS_H)

                    elif active_tool == "Text":
                        typing = True
                        text = ""
                        text_pos = (cx, cy)

                    else:
                        drawing = True
                        start_pos = (cx, cy)
                        prev_pos = (cx, cy)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:

                if drawing and start_pos is not None:
                    cx, cy = canvas_pos(mx, my, CANVAS_X)
                    end_pos = (cx, cy)

                    if active_tool in [
                        "Line", "Rectangle", "Circle", "Square",
                        "Right Triangle", "Equilateral Triangle", "Rhombus"
                    ]:
                        commit_shape(canvas, active_tool, start_pos, end_pos, draw_color, brush_size)

                drawing = False
                start_pos = None
                prev_pos = None

            if event.type == pygame.MOUSEMOTION and drawing:
                cx, cy = canvas_pos(mx, my, CANVAS_X)

                if active_tool == "Pencil":
                    if prev_pos:
                        pygame.draw.line(canvas, draw_color, prev_pos, (cx, cy), brush_size)

                    prev_pos = (cx, cy)

                elif active_tool == "Eraser":
                    pygame.draw.circle(canvas, BG_CANVAS, (cx, cy), ERASER_SIZE)

        screen.blit(canvas, (CANVAS_X, 0))

        if drawing and start_pos and active_tool in [
            "Line", "Rectangle", "Circle", "Square",
            "Right Triangle", "Equilateral Triangle", "Rhombus"
        ]:
            cx, cy = canvas_pos(mx, my, CANVAS_X)

            preview = canvas.copy()
            draw_preview(preview, active_tool, start_pos, (cx, cy), draw_color, brush_size)
            screen.blit(preview, (CANVAS_X, 0))

        if typing and active_tool == "Text" and text_pos:
            text_surface = font_text.render(text, True, draw_color)
            screen.blit(text_surface, (CANVAS_X + text_pos[0], text_pos[1]))

        if active_tool == "Eraser" and mx >= CANVAS_X:
            pygame.draw.circle(screen, (180, 180, 180), (mx, my), ERASER_SIZE, 2)

        draw_toolbar(screen, active_tool, draw_color, brush_size)

        pygame.display.flip()


if __name__ == "__main__":
    main()