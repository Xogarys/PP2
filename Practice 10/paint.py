import pygame
import sys

pygame.init()

# Window settings
WIDTH, HEIGHT = 900, 650
TOOLBAR_H = 60
CANVAS_TOP = TOOLBAR_H
CANVAS_H = HEIGHT - TOOLBAR_H

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("consolas", 15, bold=True)

# Color palette
PALETTE = [
    (255, 255, 255),   # White
    (220, 50, 50),     # Red
    (50, 180, 50),     # Green
    (50, 130, 230),    # Blue
    (255, 220, 0),     # Yellow
    (255, 140, 0),     # Orange
    (160, 32, 240),    # Purple
    (20, 200, 200),    # Cyan
]

# Tools
TOOLS = ["Pencil", "Rect", "Circle", "Eraser"]

# Toolbar sizes
TOOL_W = 80
TOOL_H = 36
SWATCH_SIZE = 28
BRUSH_SIZES = [2, 5, 10, 18]


def draw_toolbar(surface, active_tool, active_color, brush_size):
    """Draw toolbar with tools, colors and brush sizes"""

    pygame.draw.rect(surface, (40, 40, 40), (0, 0, WIDTH, TOOLBAR_H))

    # Tool buttons
    for i, tool in enumerate(TOOLS):
        x = 10 + i * (TOOL_W + 5)

        button_color = (80, 120, 200) if tool == active_tool else (70, 70, 70)

        pygame.draw.rect(
            surface,
            button_color,
            (x, 10, TOOL_W, TOOL_H),
            border_radius=5
        )

        text = font.render(tool, True, (255, 255, 255))
        surface.blit(
            text,
            (
                x + TOOL_W // 2 - text.get_width() // 2,
                10 + TOOL_H // 2 - text.get_height() // 2
            )
        )

    # Color palette
    palette_x = 10 + len(TOOLS) * (TOOL_W + 5) + 20

    for i, color in enumerate(PALETTE):
        x = palette_x + i * (SWATCH_SIZE + 5)

        pygame.draw.rect(
            surface,
            color,
            (x, 15, SWATCH_SIZE, SWATCH_SIZE),
            border_radius=4
        )

        if color == active_color:
            pygame.draw.rect(
                surface,
                (255, 255, 255),
                (x - 2, 13, SWATCH_SIZE + 4, SWATCH_SIZE + 4),
                2,
                border_radius=5
            )

    # Brush sizes
    bx = WIDTH - 180

    for i, size in enumerate(BRUSH_SIZES):
        rect = pygame.Rect(bx + i * 40, 12, 32, 32)

        button_color = (80, 120, 200) if size == brush_size else (70, 70, 70)

        pygame.draw.rect(surface, button_color, rect, border_radius=4)

        pygame.draw.circle(
            surface,
            (255, 255, 255),
            rect.center,
            max(1, size // 2)
        )


def toolbar_click(mx, my):
    """Check if toolbar was clicked"""

    if my > TOOLBAR_H:
        return None

    # Tool buttons
    for i, tool in enumerate(TOOLS):
        x = 10 + i * (TOOL_W + 5)

        if x <= mx <= x + TOOL_W and 10 <= my <= 10 + TOOL_H:
            return ("tool", tool)

    # Color palette
    palette_x = 10 + len(TOOLS) * (TOOL_W + 5) + 20

    for i, color in enumerate(PALETTE):
        x = palette_x + i * (SWATCH_SIZE + 5)

        if x <= mx <= x + SWATCH_SIZE and 15 <= my <= 15 + SWATCH_SIZE:
            return ("color", color)

    # Brush sizes
    bx = WIDTH - 180

    for i, size in enumerate(BRUSH_SIZES):
        if bx + i * 40 <= mx <= bx + i * 40 + 32 and 12 <= my <= 44:
            return ("brush", size)

    return None


def draw_shape(surface, tool, start, end, color, thickness):
    """Draw rectangle or circle"""

    x1, y1 = start
    x2, y2 = end

    if tool == "Rect":
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        pygame.draw.rect(
            surface,
            color,
            (left, top, width, height),
            thickness
        )

    elif tool == "Circle":
        rect = pygame.Rect(
            min(x1, x2),
            min(y1, y2),
            abs(x2 - x1),
            abs(y2 - y1)
        )

        if rect.width > 0 and rect.height > 0:
            pygame.draw.ellipse(
                surface,
                color,
                rect,
                thickness
            )


def main():
    # Black canvas
    canvas = pygame.Surface((WIDTH, CANVAS_H))
    canvas.fill((0, 0, 0))

    # Default settings
    active_tool = "Pencil"
    active_color = (255, 255, 255)  # draw with white
    brush_size = 5

    drawing = False
    start_pos = None
    preview = None

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Keyboard shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    canvas.fill((0, 0, 0))  # clear to black

                if event.key == pygame.K_p:
                    active_tool = "Pencil"

                if event.key == pygame.K_r:
                    active_tool = "Rect"

                if event.key == pygame.K_o:
                    active_tool = "Circle"

                if event.key == pygame.K_e:
                    active_tool = "Eraser"

            # Mouse button down
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                hit = toolbar_click(mx, my)

                if hit:
                    kind, value = hit

                    if kind == "tool":
                        active_tool = value

                    elif kind == "color":
                        active_color = value

                    elif kind == "brush":
                        brush_size = value

                else:
                    drawing = True
                    start_pos = (mx, my - CANVAS_TOP)

                    # Draw immediately for pencil and eraser
                    if active_tool == "Pencil":
                        pygame.draw.circle(
                            canvas,
                            active_color,
                            start_pos,
                            brush_size
                        )

                    elif active_tool == "Eraser":
                        pygame.draw.circle(
                            canvas,
                            (0, 0, 0),  # erase with black
                            start_pos,
                            brush_size * 2
                        )

            # Mouse button up
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and active_tool in ["Rect", "Circle"]:
                    end_pos = (event.pos[0], event.pos[1] - CANVAS_TOP)

                    draw_shape(
                        canvas,
                        active_tool,
                        start_pos,
                        end_pos,
                        active_color,
                        brush_size
                    )

                drawing = False
                preview = None

            # Mouse move
            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my = event.pos
                current_pos = (mx, my - CANVAS_TOP)

                if active_tool == "Pencil":
                    pygame.draw.line(
                        canvas,
                        active_color,
                        start_pos,
                        current_pos,
                        brush_size
                    )
                    start_pos = current_pos

                elif active_tool == "Eraser":
                    pygame.draw.line(
                        canvas,
                        (0, 0, 0),  # erase with black
                        start_pos,
                        current_pos,
                        brush_size * 3
                    )
                    start_pos = current_pos

                elif active_tool in ["Rect", "Circle"]:
                    preview = canvas.copy()

                    draw_shape(
                        preview,
                        active_tool,
                        start_pos,
                        current_pos,
                        active_color,
                        brush_size
                    )

        # Draw screen
        screen.fill((30, 30, 30))

        if preview:
            screen.blit(preview, (0, CANVAS_TOP))
        else:
            screen.blit(canvas, (0, CANVAS_TOP))

        draw_toolbar(screen, active_tool, active_color, brush_size)

        pygame.display.flip()


if __name__ == "__main__":
    main()