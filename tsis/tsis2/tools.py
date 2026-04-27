import pygame


def canvas_pos(mx, my, canvas_x):
    return mx - canvas_x, my


def flood_fill(surface, x, y, new_color, canvas_w, canvas_h):
    old_color = surface.get_at((x, y))
    new_color = pygame.Color(*new_color)

    if old_color == new_color:
        return

    stack = [(x, y)]

    while stack:
        x, y = stack.pop()

        if x < 0 or x >= canvas_w or y < 0 or y >= canvas_h:
            continue

        if surface.get_at((x, y)) == old_color:
            surface.set_at((x, y), new_color)

            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))


def draw_preview(surface, tool, start, end, color, size):
    if tool == "Line":
        pygame.draw.line(surface, color, start, end, size)

    elif tool == "Rectangle":
        x = min(start[0], end[0])
        y = min(start[1], end[1])
        w = abs(end[0] - start[0])
        h = abs(end[1] - start[1])
        pygame.draw.rect(surface, color, (x, y, w, h), size)

    elif tool == "Circle":
        center = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
        radius = min(abs(end[0] - start[0]), abs(end[1] - start[1])) // 2

        pygame.draw.circle(surface, color, center, radius, size)

    elif tool == "Square":
        side = min(abs(end[0] - start[0]), abs(end[1] - start[1]))
        pygame.draw.rect(surface, color, (start[0], start[1], side, side), size)

    elif tool == "Right Triangle":
        points = [start, (end[0], start[1]), end]
        pygame.draw.polygon(surface, color, points, size)

    elif tool == "Equilateral Triangle":
        x1, y1 = start
        x2, y2 = end

        side = abs(x2 - x1)
        height = int((3 ** 0.5 / 2) * side)

        points = [
            (x1, y1),
            (x1 + side, y1),
            (x1 + side // 2, y1 - height)
        ]

        pygame.draw.polygon(surface, color, points, size)

    elif tool == "Rhombus":
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2

        points = [
            (cx, start[1]),
            (end[0], cy),
            (cx, end[1]),
            (start[0], cy)
        ]

        pygame.draw.polygon(surface, color, points, size)


def commit_shape(canvas_surf, tool, start, end, color, size):
    draw_preview(canvas_surf, tool, start, end, color, size)