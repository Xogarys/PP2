import pygame
import sys
import math
from datetime import datetime

from tools import (
    flood_fill,
    draw_shape,
    points_right_triangle,
    points_equilateral_triangle,
    points_rhombus,
)

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()

WIDTH, HEIGHT = 1300, 720
TOOLBAR_H     = 64
HINT_H        = 20
CANVAS_TOP    = TOOLBAR_H
CANVAS_H      = HEIGHT - TOOLBAR_H - HINT_H

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint — TSIS 2")
clock  = pygame.time.Clock()

font      = pygame.font.SysFont("consolas", 13, bold=True)
font_tiny = pygame.font.SysFont("consolas", 11)
font_text = pygame.font.SysFont("consolas", 20)   # used for text tool rendering

# ── Colour palette ────────────────────────────────────────────────────────────
PALETTE = [
    (  0,   0,   0), (255, 255, 255), (220,  50,  50), ( 50, 180,  50),
    ( 50, 130, 230), (255, 220,   0), (255, 140,   0), (160,  32, 240),
    ( 20, 200, 200), (255, 105, 180), (139,  69,  19), (128, 128, 128),
]

# ── Tools ─────────────────────────────────────────────────────────────────────
TOOLS = ["Pencil", "Line", "Rect", "Square", "Circle",
         "RTri",   "EqTri", "Rhombus", "Fill", "Text", "Eraser"]

SHAPE_TOOLS   = {"Rect", "Square", "Circle", "RTri", "EqTri", "Rhombus", "Line"}

TOOL_W, TOOL_H = 60, 34
SWATCH_SIZE    = 24
BRUSH_SIZES    = [2, 5, 10, 18]

# ── Toolbar ───────────────────────────────────────────────────────────────────

def draw_toolbar(surface, active_tool, active_color, brush_size):
    pygame.draw.rect(surface, (28, 28, 35), (0, 0, WIDTH, TOOLBAR_H))
    pygame.draw.line(surface, (70, 70, 90), (0, TOOLBAR_H - 1), (WIDTH, TOOLBAR_H - 1))

    # Tool buttons
    for i, tool in enumerate(TOOLS):
        x = 4 + i * (TOOL_W + 2)
        is_active = (tool == active_tool)
        col = (60, 110, 210) if is_active else (55, 55, 68)
        pygame.draw.rect(surface, col, (x, 10, TOOL_W, TOOL_H), border_radius=5)
        if is_active:
            pygame.draw.rect(surface, (120, 160, 255),
                             (x, 10, TOOL_W, TOOL_H), 1, border_radius=5)
        lbl = font.render(tool, True, (240, 240, 255) if is_active else (180, 180, 200))
        surface.blit(lbl, (x + TOOL_W // 2 - lbl.get_width()  // 2,
                           10 + TOOL_H // 2 - lbl.get_height() // 2))

    # Colour swatches
    palette_x = 4 + len(TOOLS) * (TOOL_W + 2) + 8
    for j, c in enumerate(PALETTE):
        sx = palette_x + j * (SWATCH_SIZE + 3)
        pygame.draw.rect(surface, c, (sx, 20, SWATCH_SIZE, SWATCH_SIZE), border_radius=3)
        if c == active_color:
            pygame.draw.rect(surface, (255, 255, 255),
                             (sx - 2, 18, SWATCH_SIZE + 4, SWATCH_SIZE + 4),
                             2, border_radius=4)

    # Active colour preview
    prev_x = palette_x + len(PALETTE) * (SWATCH_SIZE + 3) + 6
    pygame.draw.rect(surface, active_color, (prev_x, 12, 36, 36), border_radius=5)
    pygame.draw.rect(surface, (160, 160, 180), (prev_x, 12, 36, 36), 2, border_radius=5)

    # Brush size buttons
    bx = WIDTH - len(BRUSH_SIZES) * 34 - 6
    for k, bs in enumerate(BRUSH_SIZES):
        r = pygame.Rect(bx + k * 34, 14, 30, 30)
        col = (60, 110, 210) if bs == brush_size else (55, 55, 68)
        pygame.draw.rect(surface, col, r, border_radius=4)
        pygame.draw.circle(surface, (240, 240, 255), r.center, max(1, bs // 2))


def toolbar_click(mx, my):
    if my >= TOOLBAR_H:
        return None

    for i, tool in enumerate(TOOLS):
        x = 4 + i * (TOOL_W + 2)
        if x <= mx <= x + TOOL_W and 10 <= my <= 10 + TOOL_H:
            return ('tool', tool)

    palette_x = 4 + len(TOOLS) * (TOOL_W + 2) + 8
    for j, c in enumerate(PALETTE):
        sx = palette_x + j * (SWATCH_SIZE + 3)
        if sx <= mx <= sx + SWATCH_SIZE and 20 <= my <= 20 + SWATCH_SIZE:
            return ('color', c)

    bx = WIDTH - len(BRUSH_SIZES) * 34 - 6
    for k, bs in enumerate(BRUSH_SIZES):
        if bx + k * 34 <= mx <= bx + k * 34 + 30 and 14 <= my <= 44:
            return ('brush', bs)

    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    canvas = pygame.Surface((WIDTH, CANVAS_H))
    canvas.fill((255, 255, 255))

    active_tool  = "Pencil"
    active_color = (0, 0, 0)
    brush_size   = 5

    drawing      = False
    start_pos    = None
    preview_surf = None

    # Text tool state
    text_mode    = False
    text_pos     = None
    text_buffer  = ""

    KEY_MAP = {
        pygame.K_p: "Pencil",
        pygame.K_l: "Line",
        pygame.K_r: "Rect",
        pygame.K_s: "Square",
        pygame.K_o: "Circle",
        pygame.K_t: "RTri",
        pygame.K_g: "EqTri",
        pygame.K_h: "Rhombus",
        pygame.K_f: "Fill",
        pygame.K_x: "Text",
        pygame.K_e: "Eraser",
    }

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── Keyboard ──────────────────────────────────────────────────
            if event.type == pygame.KEYDOWN:

                # Text tool: capture typing
                if text_mode:
                    if event.key == pygame.K_RETURN:
                        # Commit text to canvas
                        rendered = font_text.render(text_buffer, True, active_color)
                        canvas.blit(rendered, text_pos)
                        text_mode   = False
                        text_buffer = ""
                        text_pos    = None
                    elif event.key == pygame.K_ESCAPE:
                        text_mode   = False
                        text_buffer = ""
                        text_pos    = None
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            text_buffer += event.unicode
                    continue   # don't process other shortcuts while typing

                # Ctrl+S → save
                mods = pygame.key.get_mods()
                if event.key == pygame.K_s and (mods & pygame.KMOD_CTRL):
                    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
                    path = f"canvas_{ts}.png"
                    pygame.image.save(canvas, path)
                    pygame.display.set_caption(f"Paint — saved {path}")
                    continue

                if event.key == pygame.K_c and not (mods & pygame.KMOD_CTRL):
                    canvas.fill((255, 255, 255))
                elif event.key in KEY_MAP:
                    active_tool = KEY_MAP[event.key]
                    text_mode   = False
                # Brush size via 1-4 keys
                elif event.key == pygame.K_1: brush_size = BRUSH_SIZES[0]
                elif event.key == pygame.K_2: brush_size = BRUSH_SIZES[1]
                elif event.key == pygame.K_3: brush_size = BRUSH_SIZES[2]
                elif event.key == pygame.K_4: brush_size = BRUSH_SIZES[3]

            # ── Mouse press ───────────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                hit = toolbar_click(mx, my)
                if hit:
                    kind, val = hit
                    if kind == 'tool':
                        active_tool = val
                        text_mode   = False
                    if kind == 'color':  active_color = val
                    if kind == 'brush':  brush_size   = val
                else:
                    cy_off = my - CANVAS_TOP
                    if 0 <= cy_off < CANVAS_H:

                        if active_tool == "Fill":
                            flood_fill(canvas, (mx, cy_off), active_color)

                        elif active_tool == "Text":
                            # Start / restart text entry
                            text_mode   = True
                            text_pos    = (mx, cy_off)
                            text_buffer = ""

                        else:
                            # Cancel text if clicking elsewhere with another tool
                            text_mode   = False
                            text_buffer = ""
                            drawing     = True
                            start_pos   = (mx, cy_off)
                            if active_tool in ("Pencil", "Eraser"):
                                col = (255, 255, 255) if active_tool == "Eraser" \
                                      else active_color
                                pygame.draw.circle(canvas, col, start_pos, brush_size)

            # ── Mouse release ─────────────────────────────────────────────
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and active_tool in SHAPE_TOOLS:
                    mx, my  = event.pos
                    end_pos = (mx, my - CANVAS_TOP)
                    draw_shape(canvas, active_tool, start_pos, end_pos,
                               active_color, brush_size)
                drawing      = False
                preview_surf = None

            # ── Mouse drag ────────────────────────────────────────────────
            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my   = event.pos
                canvas_y = max(0, min(my - CANVAS_TOP, CANVAS_H - 1))

                if active_tool == "Pencil":
                    lx, ly = start_pos
                    pygame.draw.line(canvas, active_color,
                                     (lx, ly), (mx, canvas_y), brush_size)
                    start_pos = (mx, canvas_y)

                elif active_tool == "Eraser":
                    lx, ly = start_pos
                    pygame.draw.line(canvas, (255, 255, 255),
                                     (lx, ly), (mx, canvas_y), brush_size * 3)
                    start_pos = (mx, canvas_y)

                elif active_tool in SHAPE_TOOLS:
                    preview_surf = canvas.copy()
                    draw_shape(preview_surf, active_tool, start_pos,
                               (mx, canvas_y), active_color, brush_size)

        # ── Render ───────────────────────────────────────────────────────────
        screen.fill((18, 18, 22))

        # Canvas (or preview during shape drag)
        display_canvas = preview_surf if preview_surf else canvas

        # Text tool live preview: draw on a temp copy
        if text_mode and text_pos and text_buffer:
            display_canvas = display_canvas.copy()
            rendered = font_text.render(text_buffer + "|", True, active_color)
            display_canvas.blit(rendered, text_pos)
        elif text_mode and text_pos:
            # Draw blinking cursor placeholder
            display_canvas = display_canvas.copy()
            cursor_surf = font_text.render("|", True, active_color)
            display_canvas.blit(cursor_surf, text_pos)

        screen.blit(display_canvas, (0, CANVAS_TOP))
        draw_toolbar(screen, active_tool, active_color, brush_size)

        # Hint bar
        if text_mode:
            hint_str = f"TEXT MODE — typing: '{text_buffer}'  |  Enter=confirm  Esc=cancel"
        else:
            hint_str = ("C=clear  P=pencil  L=line  R=rect  S=square  O=circle  "
                        "T=rtri  G=eqtri  H=rhombus  F=fill  X=text  E=eraser  "
                        "1-4=brush  Ctrl+S=save")
        hint = font_tiny.render(hint_str, True, (110, 110, 140))
        screen.blit(hint, (4, HEIGHT - HINT_H + 3))

        pygame.display.flip()


if __name__ == "__main__":
    main()