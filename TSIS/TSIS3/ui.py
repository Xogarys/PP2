"""
ui.py
All non-gameplay Pygame screens: Main Menu, Leaderboard, Settings,
Username Entry, and Game Over.  Each function is a blocking loop that
returns a value indicating what should happen next.
"""

import pygame
import sys
from persistence import (load_leaderboard, load_settings, save_settings,
                          DEFAULT_SETTINGS)

# ── Colour palette ────────────────────────────────────────────────────────────
BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
GRAY    = (120, 120, 120)
DKGRAY  = ( 30,  30,  40)
PANEL   = ( 18,  18,  28)
RED     = (220,  50,  50)
BLUE    = ( 60, 140, 240)
GREEN   = ( 60, 200,  80)
YELLOW  = (255, 220,   0)
ORANGE  = (255, 140,   0)
PURPLE  = (160,  80, 240)
GOLD    = (255, 200,   0)
SILVER  = (200, 200, 210)
CYAN    = ( 80, 220, 220)
MGRAY   = ( 60,  60,  75)

# Car colour name → RGB
CAR_COLORS = {
    "blue":   (  60, 140, 240),
    "red":    ( 220,  50,  50),
    "green":  (  60, 200,  80),
    "yellow": ( 230, 200,   0),
    "purple": ( 160,  80, 240),
}

# ── Shared font cache (initialised on first import after pygame.init()) ───────
_fonts: dict = {}

def _f(key):
    """Lazy-init fonts."""
    if not _fonts:
        _fonts["big"]   = pygame.font.SysFont("consolas", 48, bold=True)
        _fonts["med"]   = pygame.font.SysFont("consolas", 28)
        _fonts["small"] = pygame.font.SysFont("consolas", 20)
        _fonts["tiny"]  = pygame.font.SysFont("consolas", 15)
    return _fonts[key]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _blit_centered(surface, text_surf, cy):
    surface.blit(text_surf,
                 (surface.get_width() // 2 - text_surf.get_width() // 2, cy))


def _draw_button(surface, rect, label, hover=False, color=MGRAY):
    col = tuple(min(255, c + 40) for c in color) if hover else color
    pygame.draw.rect(surface, col, rect, border_radius=8)
    pygame.draw.rect(surface, GRAY, rect, 2, border_radius=8)
    lbl = _f("small").render(label, True, WHITE)
    surface.blit(lbl,
                 (rect.centerx - lbl.get_width()  // 2,
                  rect.centery - lbl.get_height() // 2))


def _draw_background(surface):
    """Simple dark gradient background."""
    surface.fill(PANEL)
    w, h = surface.get_size()
    for i in range(0, h, 6):
        alpha = int(30 * i / h)
        line = pygame.Surface((w, 6), pygame.SRCALPHA)
        line.fill((40, 40, 60, alpha))
        surface.blit(line, (0, i))


# ── Username Entry ────────────────────────────────────────────────────────────

def screen_username(surface, clock) -> str:
    """
    Ask the player to type their name.
    Returns the entered name (stripped, max 16 chars).
    """
    name = ""
    W, H = surface.get_size()

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()[:16]
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable() and len(name) < 16:
                    name += event.unicode

        _draw_background(surface)
        _blit_centered(surface, _f("big").render("ENTER NAME", True, CYAN), H // 2 - 100)
        _blit_centered(surface, _f("small").render("Type your name and press Enter", True, GRAY),
                       H // 2 - 40)

        # Name box
        box = pygame.Rect(W // 2 - 150, H // 2, 300, 44)
        pygame.draw.rect(surface, MGRAY, box, border_radius=6)
        pygame.draw.rect(surface, CYAN, box, 2, border_radius=6)
        name_surf = _f("med").render(name + ("_" if pygame.time.get_ticks() % 800 < 400 else " "),
                                     True, WHITE)
        surface.blit(name_surf, (box.x + 8, box.y + 8))

        pygame.display.flip()


# ── Main Menu ─────────────────────────────────────────────────────────────────

def screen_main_menu(surface, clock) -> str:
    """
    Returns: 'play' | 'leaderboard' | 'settings' | 'quit'
    """
    W, H = surface.get_size()
    buttons = [
        ("▶  PLAY",        "play"),
        ("🏆  LEADERBOARD", "leaderboard"),
        ("⚙  SETTINGS",    "settings"),
        ("✕  QUIT",        "quit"),
    ]
    btn_w, btn_h = 260, 50
    btn_x = W // 2 - btn_w // 2
    rects = [pygame.Rect(btn_x, H // 2 - 30 + i * 64, btn_w, btn_h)
             for i in range(len(buttons))]

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, (_, action) in zip(rects, buttons):
                    if rect.collidepoint(mx, my):
                        return action

        _draw_background(surface)

        # Title
        t1 = _f("big").render("🏎  RACER", True, YELLOW)
        _blit_centered(surface, t1, H // 2 - 180)
        t2 = _f("small").render("Advanced Edition", True, ORANGE)
        _blit_centered(surface, t2, H // 2 - 120)

        for rect, (label, _) in zip(rects, buttons):
            _draw_button(surface, rect, label, hover=rect.collidepoint(mx, my))

        pygame.display.flip()


# ── Settings Screen ───────────────────────────────────────────────────────────

def screen_settings(surface, clock) -> dict:
    """
    Let the player toggle sound, pick car colour, choose difficulty.
    Returns the (possibly modified) settings dict.
    """
    W, H = surface.get_size()
    settings = load_settings()

    COLOR_NAMES  = list(CAR_COLORS.keys())
    DIFF_NAMES   = ["easy", "normal", "hard"]

    back_rect = pygame.Rect(W // 2 - 100, H - 80, 200, 44)

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(mx, my):
                    save_settings(settings)
                    return settings

                # Sound toggle
                if sound_rect.collidepoint(mx, my):
                    settings["sound"] = not settings["sound"]

                # Car colour cycle
                if color_left.collidepoint(mx, my):
                    idx = COLOR_NAMES.index(settings["car_color"])
                    settings["car_color"] = COLOR_NAMES[(idx - 1) % len(COLOR_NAMES)]
                if color_right.collidepoint(mx, my):
                    idx = COLOR_NAMES.index(settings["car_color"])
                    settings["car_color"] = COLOR_NAMES[(idx + 1) % len(COLOR_NAMES)]

                # Difficulty cycle
                if diff_left.collidepoint(mx, my):
                    idx = DIFF_NAMES.index(settings["difficulty"])
                    settings["difficulty"] = DIFF_NAMES[(idx - 1) % len(DIFF_NAMES)]
                if diff_right.collidepoint(mx, my):
                    idx = DIFF_NAMES.index(settings["difficulty"])
                    settings["difficulty"] = DIFF_NAMES[(idx + 1) % len(DIFF_NAMES)]

        _draw_background(surface)
        _blit_centered(surface, _f("big").render("SETTINGS", True, CYAN), 40)

        row_y = 160

        # ── Sound ──
        _blit_centered(surface,
                       _f("small").render("Sound", True, GRAY), row_y)
        state_lbl = "ON" if settings["sound"] else "OFF"
        state_col = GREEN if settings["sound"] else RED
        sound_rect = pygame.Rect(W // 2 - 60, row_y + 30, 120, 38)
        pygame.draw.rect(surface, MGRAY, sound_rect, border_radius=6)
        pygame.draw.rect(surface, state_col, sound_rect, 2, border_radius=6)
        sl = _f("med").render(state_lbl, True, state_col)
        surface.blit(sl, (sound_rect.centerx - sl.get_width() // 2,
                          sound_rect.centery - sl.get_height() // 2))

        row_y += 110

        # ── Car colour ──
        _blit_centered(surface,
                       _f("small").render("Car Color", True, GRAY), row_y)
        color_left  = pygame.Rect(W // 2 - 130, row_y + 30, 40, 38)
        color_right = pygame.Rect(W // 2 +  90, row_y + 30, 40, 38)
        _draw_button(surface, color_left,  "◀", color_left.collidepoint(mx, my))
        _draw_button(surface, color_right, "▶", color_right.collidepoint(mx, my))
        cc = CAR_COLORS[settings["car_color"]]
        color_box = pygame.Rect(W // 2 - 80, row_y + 30, 160, 38)
        pygame.draw.rect(surface, cc, color_box, border_radius=6)
        pygame.draw.rect(surface, WHITE, color_box, 2, border_radius=6)
        cn = _f("small").render(settings["car_color"].upper(), True, BLACK)
        surface.blit(cn, (color_box.centerx - cn.get_width() // 2,
                          color_box.centery - cn.get_height() // 2))

        row_y += 110

        # ── Difficulty ──
        _blit_centered(surface,
                       _f("small").render("Difficulty", True, GRAY), row_y)
        diff_left  = pygame.Rect(W // 2 - 130, row_y + 30, 40, 38)
        diff_right = pygame.Rect(W // 2 +  90, row_y + 30, 40, 38)
        _draw_button(surface, diff_left,  "◀", diff_left.collidepoint(mx, my))
        _draw_button(surface, diff_right, "▶", diff_right.collidepoint(mx, my))
        diff_col = {
            "easy": GREEN, "normal": YELLOW, "hard": RED
        }[settings["difficulty"]]
        diff_box = pygame.Rect(W // 2 - 80, row_y + 30, 160, 38)
        pygame.draw.rect(surface, MGRAY, diff_box, border_radius=6)
        pygame.draw.rect(surface, diff_col, diff_box, 2, border_radius=6)
        dn = _f("small").render(settings["difficulty"].upper(), True, diff_col)
        surface.blit(dn, (diff_box.centerx - dn.get_width() // 2,
                          diff_box.centery - dn.get_height() // 2))

        _draw_button(surface, back_rect, "◀  BACK",
                     back_rect.collidepoint(mx, my), color=(40, 60, 80))
        pygame.display.flip()


# ── Leaderboard Screen ────────────────────────────────────────────────────────

def screen_leaderboard(surface, clock) -> None:
    """Display top-10 scores. Returns when Back is pressed."""
    W, H = surface.get_size()
    back_rect = pygame.Rect(W // 2 - 100, H - 70, 200, 44)
    RANK_COLORS = [GOLD, SILVER, (180, 100, 30)] + [WHITE] * 7

    while True:
        clock.tick(60)
        entries = load_leaderboard()
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(mx, my):
                    return

        _draw_background(surface)
        _blit_centered(surface, _f("big").render("LEADERBOARD", True, GOLD), 30)

        header = _f("tiny").render(
            f"{'#':<3} {'Name':<16} {'Score':>7}  {'Dist':>6}  {'Coins':>5}", True, GRAY)
        _blit_centered(surface, header, 100)
        pygame.draw.line(surface, MGRAY,
                         (W // 2 - 200, 120), (W // 2 + 200, 120), 1)

        for i, e in enumerate(entries[:10]):
            col = RANK_COLORS[i]
            row = (f"{i+1:<3} {e['name']:<16} {e['score']:>7}  "
                   f"{e['distance']:>5}m  {e['coins']:>5}")
            surf = _f("tiny").render(row, True, col)
            _blit_centered(surface, surf, 130 + i * 34)

        if not entries:
            _blit_centered(surface,
                           _f("small").render("No scores yet — play a game!", True, GRAY),
                           300)

        _draw_button(surface, back_rect, "◀  BACK",
                     back_rect.collidepoint(mx, my), color=(40, 60, 80))
        pygame.display.flip()


# ── Game-Over Screen ──────────────────────────────────────────────────────────

def screen_game_over(surface, clock,
                     score: int, distance: int, coins: int) -> str:
    """
    Show end-of-run stats.
    Returns: 'retry' | 'menu'
    """
    W, H = surface.get_size()
    retry_rect = pygame.Rect(W // 2 - 130, H // 2 + 100, 120, 46)
    menu_rect  = pygame.Rect(W // 2 +  10, H // 2 + 100, 120, 46)

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_rect.collidepoint(mx, my): return "retry"
                if menu_rect.collidepoint(mx, my):  return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return "retry"
                if event.key == pygame.K_m: return "menu"

        _draw_background(surface)

        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 130))
        surface.blit(ov, (0, 0))

        _blit_centered(surface,
                       _f("big").render("GAME OVER", True, RED), H // 2 - 140)

        for lbl, val, col in [
            (f"Score:    {score}",      None, WHITE),
            (f"Distance: {distance} m", None, CYAN),
            (f"Coins:    {coins} pts",  None, GOLD),
        ]:
            _blit_centered(surface, _f("med").render(lbl, True, col),
                           H // 2 - 60 + [0, 40, 80][[WHITE, CYAN, GOLD].index(col)])

        _blit_centered(surface, _f("tiny").render("R = retry   M = menu", True, GRAY),
                       H // 2 + 90)

        _draw_button(surface, retry_rect, "↺ RETRY",
                     retry_rect.collidepoint(mx, my), color=(40, 80, 40))
        _draw_button(surface, menu_rect, "⌂ MENU",
                     menu_rect.collidepoint(mx, my), color=(60, 40, 80))
        pygame.display.flip()
