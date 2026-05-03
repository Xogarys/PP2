"""
tools.py — Drawing helpers for Paint (TSIS 2)

Exports:
    flood_fill(surface, pos, fill_color)
    draw_shape(surface, tool, p1, p2, color, thickness)
    points_right_triangle(p1, p2)
    points_equilateral_triangle(p1, p2)
    points_rhombus(p1, p2)
"""

import math
import pygame
from collections import deque


# ─────────────────────────────────────────────────────────────────────────────
# Flood fill
# ─────────────────────────────────────────────────────────────────────────────

def flood_fill(surface: pygame.Surface,
               pos: tuple[int, int],
               fill_color: tuple[int, int, int]) -> None:
    """
    BFS flood fill.

    Replaces all pixels reachable from *pos* that share the same colour
    as the pixel at *pos* with *fill_color*.  Uses exact colour matching.
    """
    x0, y0 = int(pos[0]), int(pos[1])
    w, h   = surface.get_size()

    if not (0 <= x0 < w and 0 <= y0 < h):
        return

    target = surface.get_at((x0, y0))[:3]   # ignore alpha
    fill   = fill_color[:3]

    if target == fill:
        return

    # Lock for pixel-level access
    surface.lock()

    visited = [[False] * h for _ in range(w)]
    queue   = deque()
    queue.append((x0, y0))
    visited[x0][y0] = True

    while queue:
        x, y = queue.popleft()
        surface.set_at((x, y), fill)

        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not visited[nx][ny]:
                if surface.get_at((nx, ny))[:3] == target:
                    visited[nx][ny] = True
                    queue.append((nx, ny))

    surface.unlock()


# ─────────────────────────────────────────────────────────────────────────────
# Geometry helpers
# ─────────────────────────────────────────────────────────────────────────────

def points_right_triangle(p1, p2):
    """
    Right-angle triangle.  Right angle sits at p1.
    Returns 3 (x, y) vertex tuples.
    """
    x1, y1 = p1
    x2, y2 = p2
    return [(x1, y1), (x2, y1), (x1, y2)]


def points_equilateral_triangle(p1, p2):
    """
    Equilateral triangle with base edge from p1 to p2.
    Returns 3 (x, y) vertex tuples.
    """
    x1, y1 = p1
    x2, y2 = p2
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2
    base = math.hypot(x2 - x1, y2 - y1)
    if base == 0:
        return [(x1, y1), (x2, y2), (x1, y1)]
    height = base * math.sqrt(3) / 2
    dx = (x2 - x1) / base
    dy = (y2 - y1) / base
    apex = (mx + dy * height, my - dx * height)
    return [(x1, y1), (x2, y2), apex]


def points_rhombus(p1, p2):
    """
    Rhombus (diamond) inscribed in the bounding box [p1, p2].
    Returns 4 (x, y) vertex tuples (top, right, bottom, left).
    """
    x1, y1 = p1
    x2, y2 = p2
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    return [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]


# ─────────────────────────────────────────────────────────────────────────────
# Unified shape drawing
# ─────────────────────────────────────────────────────────────────────────────

def draw_shape(surface, tool: str, p1, p2, color, thickness: int) -> None:
    """
    Draw *tool* onto *surface* between anchor points p1 and p2.

    Supported tools:
        Line, Rect, Square, Circle, RTri, EqTri, Rhombus
    """
    x1, y1 = p1
    x2, y2 = p2

    if tool == "Line":
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), thickness)

    elif tool == "Rect":
        left = min(x1, x2); top = min(y1, y2)
        w    = abs(x2 - x1); h  = abs(y2 - y1)
        if w > 0 and h > 0:
            pygame.draw.rect(surface, color, (left, top, w, h), thickness)

    elif tool == "Square":
        side = min(abs(x2 - x1), abs(y2 - y1))
        sx   = x1 if x2 >= x1 else x1 - side
        sy   = y1 if y2 >= y1 else y1 - side
        if side > 0:
            pygame.draw.rect(surface, color, (sx, sy, side, side), thickness)

    elif tool == "Circle":
        cx = (x1 + x2) // 2; cy = (y1 + y2) // 2
        rx = abs(x2 - x1) // 2; ry = abs(y2 - y1) // 2
        if rx > 0 and ry > 0:
            pygame.draw.ellipse(surface, color,
                                (cx - rx, cy - ry, rx * 2, ry * 2), thickness)

    elif tool == "RTri":
        pts = points_right_triangle(p1, p2)
        if len(set(pts)) > 1:
            pygame.draw.polygon(surface, color, pts, thickness)

    elif tool == "EqTri":
        pts = points_equilateral_triangle(p1, p2)
        pygame.draw.polygon(surface, color, pts, thickness)

    elif tool == "Rhombus":
        pts = points_rhombus(p1, p2)
        pygame.draw.polygon(surface, color, pts, thickness)
