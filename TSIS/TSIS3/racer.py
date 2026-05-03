"""
racer.py
Core gameplay loop for the extended Racer game.
Builds on the base from Practice 10–11 and adds:
  • Lane hazards (oil spills, slow zones)
  • Road events (nitro strips, moving barriers, speed bumps)
  • Dynamic traffic & safe-spawn logic
  • Power-ups: Nitro, Shield, Repair
  • Difficulty scaling
  • HUD with active power-up / remaining time
  • Distance meter and coins tally
"""

import pygame
import random
import sys
import math

# ── Colours ───────────────────────────────────────────────────────────────────
BLACK   = (  0,   0,   0)
WHITE   = (255, 255, 255)
GRAY    = (100, 100, 100)
DKGRAY  = ( 50,  50,  50)
GREEN   = ( 50, 160,  50)
RED     = (220,  50,  50)
BLUE    = ( 60, 140, 240)
YELLOW  = (255, 220,   0)
ORANGE  = (255, 140,   0)
CYAN    = ( 80, 220, 220)
PURPLE  = (160,  80, 240)
GOLD    = (255, 200,   0)
SILVER  = (200, 200, 210)
BRONZE  = (180, 100,  30)
LIME    = (120, 255,  80)
PINK    = (255,  80, 160)

FPS = 60

# Road geometry
ROAD_LEFT  = 80
ROAD_RIGHT = 420
ROAD_W     = ROAD_RIGHT - ROAD_LEFT

LANES = [
    ROAD_LEFT + ROAD_W // 6,
    ROAD_LEFT + ROAD_W // 2,
    ROAD_LEFT + ROAD_W * 5 // 6,
]

# Speed-boost mechanics (from Practice 11)
COINS_PER_BOOST = 5
ENEMY_BOOST     = 0.8

# Coin tier definitions
COIN_TYPES = [
    (1,  BRONZE, (120, 70, 20),    "1"),
    (3,  SILVER, (150, 150, 160),  "3"),
    (5,  GOLD,   (200, 160,   0),  "5"),
]
COIN_SPAWN_WEIGHTS = [0.60, 0.28, 0.12]

# Difficulty multipliers
DIFFICULTY = {
    "easy":   {"speed_mult": 0.75, "enemy_mult": 0.6,  "hazard_mult": 0.5},
    "normal": {"speed_mult": 1.00, "enemy_mult": 1.0,  "hazard_mult": 1.0},
    "hard":   {"speed_mult": 1.35, "enemy_mult": 1.5,  "hazard_mult": 1.6},
}

# Car colour name → RGB (mirror of ui.py without importing ui here)
CAR_COLORS = {
    "blue":   ( 60, 140, 240),
    "red":    (220,  50,  50),
    "green":  ( 60, 200,  80),
    "yellow": (230, 200,   0),
    "purple": (160,  80, 240),
}


# ── Font cache ─────────────────────────────────────────────────────────────────
_font_cache: dict = {}

def _f(key):
    if not _font_cache:
        _font_cache["big"]   = pygame.font.SysFont("consolas", 42, bold=True)
        _font_cache["med"]   = pygame.font.SysFont("consolas", 26)
        _font_cache["small"] = pygame.font.SysFont("consolas", 20)
        _font_cache["tiny"]  = pygame.font.SysFont("consolas", 14, bold=True)
    return _font_cache[key]


# ── Utility ───────────────────────────────────────────────────────────────────

def _player_safe(player, x, y, margin=120):
    """True if (x, y) is far enough from the player to be a safe spawn point."""
    return abs(x - player.x) > 60 or abs(y - player.y) > margin


# ══════════════════════════════════════════════════════════════════════════════
# Game Objects
# ══════════════════════════════════════════════════════════════════════════════

class Car:
    """Rectangle car with windscreen highlight."""
    W, H = 40, 70

    def __init__(self, lane, color, y=None):
        self.lane  = lane
        self.color = color
        self.x     = LANES[lane] - self.W // 2
        self.y     = float(y if y is not None else 720)
        self.speed = 0

    def draw(self, surface, shield=False):
        rect = pygame.Rect(self.x, int(self.y), self.W, self.H)
        pygame.draw.rect(surface, self.color, rect, border_radius=6)
        ws = pygame.Rect(self.x + 5, int(self.y) + 8, self.W - 10, 16)
        pygame.draw.rect(surface, (180, 220, 255), ws, border_radius=3)
        if shield:
            shield_rect = rect.inflate(10, 10)
            pygame.draw.rect(surface, CYAN, shield_rect, 3, border_radius=10)

    def get_rect(self):
        return pygame.Rect(self.x, int(self.y), self.W, self.H)


class Coin:
    RADIUS = 13

    def __init__(self, road_speed):
        self.lane  = random.randint(0, 2)
        self.x     = LANES[self.lane]
        self.y     = float(-self.RADIUS * 2)
        self.speed = road_speed
        self.collected = False
        tier = random.choices(COIN_TYPES, weights=COIN_SPAWN_WEIGHTS)[0]
        self.value, self.face_color, self.ring_color, self.label = tier

    def update(self): self.y += self.speed

    def draw(self, surface):
        if self.collected: return
        cx, cy = self.x, int(self.y)
        pygame.draw.circle(surface, self.ring_color, (cx, cy), self.RADIUS)
        pygame.draw.circle(surface, self.face_color, (cx, cy), self.RADIUS - 3)
        lbl = _f("tiny").render(self.label, True, BLACK)
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))

    def get_rect(self):
        r = self.RADIUS
        return pygame.Rect(self.x - r, int(self.y) - r, r * 2, r * 2)

    def is_off_screen(self): return self.y > 720 + self.RADIUS * 2


# ── Lane Hazard (oil spill / slow zone) ──────────────────────────────────────

class LaneHazard:
    """
    A rectangular hazard occupying one lane.
    Types:
      'oil'  – slippery patch: touching it forces a random lane swap
      'slow' – mud/gravel:    touching it halves road_speed for 1 s
    """
    W, H_RANGE = 60, (60, 120)

    TYPE_PROPS = {
        "oil":  {"color": (20, 20, 60),  "ring": (60, 60, 180),  "label": "OIL"},
        "slow": {"color": (80, 50, 20),  "ring": (160, 110, 40), "label": "MUD"},
    }

    def __init__(self, road_speed, player):
        self.htype = random.choice(["oil", "slow"])
        self.lane  = random.randint(0, 2)
        self.x     = LANES[self.lane] - self.W // 2
        self.h     = random.randint(*self.H_RANGE)
        self.y     = float(-self.h - 20)
        self.speed = road_speed
        self.props = self.TYPE_PROPS[self.htype]
        self.triggered = False  # only trigger once per pass

    def update(self): self.y += self.speed

    def draw(self, surface):
        rect = pygame.Rect(self.x, int(self.y), self.W, self.h)
        pygame.draw.rect(surface, self.props["color"], rect, border_radius=8)
        pygame.draw.rect(surface, self.props["ring"], rect, 3, border_radius=8)
        lbl = _f("tiny").render(self.props["label"], True, self.props["ring"])
        surface.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                           rect.centery - lbl.get_height() // 2))

    def get_rect(self):
        return pygame.Rect(self.x, int(self.y), self.W, self.h)

    def is_off_screen(self): return self.y > 720 + self.h


# ── Road Event: Nitro Strip ───────────────────────────────────────────────────

class NitroStrip:
    """
    Full-width glowing strip. Touching it gives a brief road-speed boost.
    """
    H = 18

    def __init__(self, road_speed):
        self.y     = float(-self.H - 10)
        self.speed = road_speed
        self.boost = road_speed * 0.6   # how much extra speed is added
        self.triggered = False
        self.glow  = 0   # animation counter

    def update(self):
        self.y    += self.speed
        self.glow += 0.15

    def draw(self, surface):
        alpha = int(200 + 55 * math.sin(self.glow))
        col   = (min(255, alpha), min(255, 100 + alpha // 4), 0)
        rect  = pygame.Rect(ROAD_LEFT + 8, int(self.y), ROAD_W - 16, self.H)
        pygame.draw.rect(surface, col, rect, border_radius=4)
        lbl = _f("tiny").render("NITRO ▶▶", True, BLACK)
        surface.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                           rect.centery - lbl.get_height() // 2))

    def get_rect(self):
        return pygame.Rect(ROAD_LEFT + 8, int(self.y), ROAD_W - 16, self.H)

    def is_off_screen(self): return self.y > 720 + self.H


# ── Road Event: Moving Barrier ────────────────────────────────────────────────

class MovingBarrier:
    """
    A horizontal barrier that slides left-right across the road.
    The player must dodge it.
    """
    W, H = 90, 22

    def __init__(self, road_speed):
        self.y      = float(-self.H - 20)
        self.speed  = road_speed
        self.lateral_speed = random.choice([-2.0, 2.0])
        self.x      = float(ROAD_LEFT + random.randint(0, ROAD_W - self.W))

    def update(self):
        self.y += self.speed
        self.x += self.lateral_speed
        if self.x <= ROAD_LEFT or self.x + self.W >= ROAD_RIGHT:
            self.lateral_speed *= -1

    def draw(self, surface):
        rect = pygame.Rect(int(self.x), int(self.y), self.W, self.H)
        pygame.draw.rect(surface, (200, 60, 20), rect, border_radius=4)
        pygame.draw.rect(surface, YELLOW,        rect, 3, border_radius=4)
        for i in range(0, self.W, 18):
            stripe = pygame.Rect(int(self.x) + i, int(self.y), 9, self.H)
            pygame.draw.rect(surface, BLACK, stripe)

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def is_off_screen(self): return self.y > 720 + self.H


# ── Road Event: Speed Bump ────────────────────────────────────────────────────

class SpeedBump:
    """Static bump that doesn't kill — it shakes the camera and scores 0."""
    H = 14

    def __init__(self, road_speed):
        self.y     = float(-self.H - 10)
        self.speed = road_speed
        self.triggered = False

    def update(self): self.y += self.speed

    def draw(self, surface):
        rect = pygame.Rect(ROAD_LEFT + 8, int(self.y), ROAD_W - 16, self.H)
        pygame.draw.rect(surface, (180, 180, 60), rect, border_radius=3)
        lbl = _f("tiny").render("BUMP", True, BLACK)
        surface.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                           rect.centery - lbl.get_height() // 2))

    def get_rect(self):
        return pygame.Rect(ROAD_LEFT + 8, int(self.y), ROAD_W - 16, self.H)

    def is_off_screen(self): return self.y > 720 + self.H


# ── Pothole obstacle ──────────────────────────────────────────────────────────

class Pothole:
    """Circular obstacle; hitting one ends the run (no shield bypass)."""
    RADIUS = 18

    def __init__(self, road_speed, player):
        self.lane  = random.randint(0, 2)
        self.x     = LANES[self.lane]
        self.y     = float(-self.RADIUS * 2)
        self.speed = road_speed

    def update(self): self.y += self.speed

    def draw(self, surface):
        cx, cy = self.x, int(self.y)
        pygame.draw.circle(surface, (30, 30, 30), (cx, cy), self.RADIUS)
        pygame.draw.circle(surface, (60, 40, 20), (cx, cy), self.RADIUS, 4)
        lbl = _f("tiny").render("⚠", True, YELLOW)
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))

    def get_rect(self):
        r = self.RADIUS
        return pygame.Rect(self.x - r, int(self.y) - r, r * 2, r * 2)

    def is_off_screen(self): return self.y > 720 + self.RADIUS * 2


# ── Power-Up ──────────────────────────────────────────────────────────────────

POWERUP_TYPES = {
    "nitro":  {"color": ORANGE, "label": "N", "ring": (255, 200, 0)},
    "shield": {"color": CYAN,   "label": "S", "ring": (0, 200, 200)},
    "repair": {"color": LIME,   "label": "R", "ring": (0, 160, 0)},
}
POWERUP_LIFETIME = 8.0   # seconds before it disappears if uncollected
POWERUP_RADIUS   = 16

class PowerUp:
    def __init__(self, road_speed):
        self.ptype    = random.choice(list(POWERUP_TYPES.keys()))
        self.lane     = random.randint(0, 2)
        self.x        = LANES[self.lane]
        self.y        = float(-POWERUP_RADIUS * 2)
        self.speed    = road_speed
        self.props    = POWERUP_TYPES[self.ptype]
        self.collected = False
        self.life     = POWERUP_LIFETIME * FPS   # frames until auto-remove

    def update(self):
        self.y   += self.speed
        self.life -= 1

    def draw(self, surface):
        if self.collected: return
        cx, cy = self.x, int(self.y)
        pulse = int(200 + 55 * math.sin(pygame.time.get_ticks() / 180))
        ring  = tuple(min(255, c + pulse // 4) for c in self.props["ring"])
        pygame.draw.circle(surface, ring,          (cx, cy), POWERUP_RADIUS + 3)
        pygame.draw.circle(surface, self.props["color"], (cx, cy), POWERUP_RADIUS)
        lbl = _f("tiny").render(self.props["label"], True, BLACK)
        surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))

    def get_rect(self):
        r = POWERUP_RADIUS
        return pygame.Rect(self.x - r, int(self.y) - r, r * 2, r * 2)

    def is_gone(self):
        return self.y > 720 + POWERUP_RADIUS * 2 or self.life <= 0 or self.collected


# ══════════════════════════════════════════════════════════════════════════════
# Road Drawing
# ══════════════════════════════════════════════════════════════════════════════

def draw_road(surface, stripe_offset, shake=0):
    H = surface.get_height()
    dy = random.randint(-shake, shake) if shake else 0
    surface.fill((40, 120, 40))   # grass
    pygame.draw.rect(surface, DKGRAY, (ROAD_LEFT, dy, ROAD_W, H))
    pygame.draw.rect(surface, GRAY,   (ROAD_LEFT,      dy, 8, H))
    pygame.draw.rect(surface, GRAY,   (ROAD_RIGHT - 8, dy, 8, H))
    stripe_h, gap = 40, 30
    period = stripe_h + gap
    for lx in [LANES[0] + Car.W // 2 + 10, LANES[1] + Car.W // 2 + 10]:
        for top in range(-period + int(stripe_offset) % period, H + period, period):
            pygame.draw.rect(surface, WHITE, (lx, top + dy, 4, stripe_h))


# ══════════════════════════════════════════════════════════════════════════════
# HUD
# ══════════════════════════════════════════════════════════════════════════════

_HUD_PU_COLORS = {
    "nitro":  ORANGE,
    "shield": CYAN,
    "repair": LIME,
    None:     GRAY,
}

def draw_hud(surface, score, coin_score, boost_level, coins_to_next,
             distance, active_pu, pu_timer):
    W = surface.get_width()
    # Score / coins
    surface.blit(_f("small").render(f"Score: {score}", True, WHITE),
                 (ROAD_LEFT + 6, 8))
    coins_lbl = f"Coins: {coin_score} pts"
    surface.blit(_f("small").render(coins_lbl, True, GOLD),
                 (W - _f("small").size(coins_lbl)[0] - 10, 8))

    boost_lbl = f"Boost lv: {boost_level}"
    surface.blit(_f("small").render(boost_lbl, True, ORANGE),
                 (W - _f("small").size(boost_lbl)[0] - 10, 30))

    # Boost progress bar
    filled = COINS_PER_BOOST - coins_to_next
    bar_w = 80; bar_x = W - bar_w - 10; bar_y = 54
    pygame.draw.rect(surface, GRAY,   (bar_x, bar_y, bar_w, 6))
    pygame.draw.rect(surface, ORANGE, (bar_x, bar_y,
                                       int(bar_w * filled / COINS_PER_BOOST), 6))

    # Distance
    dist_lbl = f"Dist: {distance} m"
    surface.blit(_f("small").render(dist_lbl, True, CYAN),
                 (ROAD_LEFT + 6, 30))

    # Active power-up
    if active_pu:
        col      = _HUD_PU_COLORS[active_pu]
        secs_left = max(0, pu_timer / FPS)
        pu_lbl   = f"{active_pu.upper()} {secs_left:.1f}s"
        surf     = _f("small").render(pu_lbl, True, col)
        px       = W // 2 - surf.get_width() // 2
        pygame.draw.rect(surface, (0, 0, 0, 120),
                         (px - 6, 52, surf.get_width() + 12, surf.get_height() + 4))
        surface.blit(surf, (px, 54))


# ══════════════════════════════════════════════════════════════════════════════
# Main game() function
# ══════════════════════════════════════════════════════════════════════════════

def game(screen, clock, settings: dict, player_name: str) -> dict:
    """
    Run one full race.
    Returns a result dict:
      { score, distance, coins, coin_count }
    """
    W, H = screen.get_size()
    diff     = settings.get("difficulty", "normal")
    dm       = DIFFICULTY[diff]
    car_rgb  = CAR_COLORS.get(settings.get("car_color", "blue"), BLUE)

    # ── State ────────────────────────────────────────────────────────────────
    player        = Car(lane=1, color=car_rgb, y=H - Car.H - 20)
    enemies       = []
    coins         = []
    hazards       = []   # oil spills, slow zones
    road_events   = []   # nitro strips, barriers, speed bumps
    obstacles     = []   # potholes
    powerups      = []   # collectible power-ups

    road_speed    = 5.0 * dm["speed_mult"]
    stripe_offset = 0.0
    frame         = 0

    score         = 0
    coin_score    = 0
    coin_count    = 0
    boost_level   = 0
    coins_to_next = COINS_PER_BOOST

    # Power-up state
    active_pu   = None   # "nitro" | "shield" | "repair" | None
    pu_timer    = 0      # frames remaining

    # Slow-zone effect
    slow_timer  = 0      # frames remaining when mud is active

    # Shake
    shake_timer = 0

    # Timers for spawning
    enemy_timer   = 0
    coin_timer    = 0
    hazard_timer  = 0
    event_timer   = 0
    obst_timer    = 0
    pu_timer_spawn= 0

    def base_speed():
        return 5.0 * dm["speed_mult"] + frame / 400.0 + boost_level * ENEMY_BOOST

    while True:
        clock.tick(FPS)
        frame += 1

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a) and player.lane > 0:
                    player.lane -= 1
                    player.x = LANES[player.lane] - Car.W // 2
                if event.key in (pygame.K_RIGHT, pygame.K_d) and player.lane < 2:
                    player.lane += 1
                    player.x = LANES[player.lane] - Car.W // 2

        # ── Road speed ────────────────────────────────────────────────────────
        road_speed = base_speed()
        if slow_timer > 0:
            slow_timer  -= 1
            road_speed  *= 0.5
        if active_pu == "nitro" and pu_timer > 0:
            road_speed  *= 1.6
        stripe_offset += road_speed

        # ── Power-up countdown ────────────────────────────────────────────────
        if active_pu and active_pu != "shield":
            pu_timer -= 1
            if pu_timer <= 0:
                active_pu = None

        # ── Score & distance ──────────────────────────────────────────────────
        score    += 1
        distance  = score // 10   # metres

        # ── Spawn enemies ─────────────────────────────────────────────────────
        enemy_timer += 1
        enemy_interval = max(25, int((90 - frame // 120) / dm["enemy_mult"]))
        if enemy_timer >= enemy_interval:
            enemy_timer = 0
            lane = random.randint(0, 2)
            e = Car(lane=lane,
                    color=random.choice([RED, ORANGE, WHITE]),
                    y=-Car.H - 10)
            e.speed = road_speed + random.uniform(0.5, 2.5)
            if _player_safe(player, e.x, H):
                enemies.append(e)

        # ── Spawn coins ───────────────────────────────────────────────────────
        coin_timer += 1
        if coin_timer >= random.randint(80, 190):
            coin_timer = 0
            coins.append(Coin(road_speed))

        # ── Spawn lane hazards ────────────────────────────────────────────────
        hazard_timer += 1
        hazard_interval = max(180, int(350 / dm["hazard_mult"]))
        if hazard_timer >= hazard_interval:
            hazard_timer = random.randint(-30, 30)
            hazards.append(LaneHazard(road_speed, player))

        # ── Spawn road events ─────────────────────────────────────────────────
        event_timer += 1
        if event_timer >= random.randint(280, 500):
            event_timer = 0
            choice = random.choices(
                ["nitro", "barrier", "bump"],
                weights=[0.35, 0.35, 0.30]
            )[0]
            if choice == "nitro":
                road_events.append(NitroStrip(road_speed))
            elif choice == "barrier":
                road_events.append(MovingBarrier(road_speed))
            else:
                road_events.append(SpeedBump(road_speed))

        # ── Spawn potholes ────────────────────────────────────────────────────
        obst_timer += 1
        if obst_timer >= max(200, int(420 / dm["hazard_mult"])):
            obst_timer = random.randint(-40, 40)
            obstacles.append(Pothole(road_speed, player))

        # ── Spawn power-ups ───────────────────────────────────────────────────
        pu_timer_spawn += 1
        if pu_timer_spawn >= random.randint(360, 600):
            pu_timer_spawn = 0
            powerups.append(PowerUp(road_speed))

        # ── Update all objects ────────────────────────────────────────────────
        for e in enemies: e.y += e.speed
        enemies = [e for e in enemies if e.y < H + Car.H]

        for c in coins:  c.update()
        coins = [c for c in coins if not c.is_off_screen() and not c.collected]

        for hz in hazards: hz.update()
        hazards = [hz for hz in hazards if not hz.is_off_screen()]

        for re in road_events: re.update()
        road_events = [re for re in road_events if not re.is_off_screen()]

        for ob in obstacles: ob.update()
        obstacles = [ob for ob in obstacles if not ob.is_off_screen()]

        for pu in powerups: pu.update()
        powerups = [pu for pu in powerups if not pu.is_gone()]

        if shake_timer > 0: shake_timer -= 1

        # ── Collision detection ───────────────────────────────────────────────
        pr = player.get_rect()

        # Enemy cars
        for e in enemies:
            if pr.colliderect(e.get_rect()):
                if active_pu == "shield":
                    active_pu = None
                    shake_timer = 10
                    enemies.remove(e)
                    break
                else:
                    return {"score": score, "distance": distance,
                            "coins": coin_score, "coin_count": coin_count}

        # Moving barriers
        for re in road_events:
            if isinstance(re, MovingBarrier) and pr.colliderect(re.get_rect()):
                if active_pu == "shield":
                    active_pu = None
                    shake_timer = 10
                else:
                    return {"score": score, "distance": distance,
                            "coins": coin_score, "coin_count": coin_count}

        # Potholes
        for ob in obstacles:
            if pr.colliderect(ob.get_rect()):
                if active_pu == "repair":
                    active_pu = None
                    obstacles.remove(ob)
                    shake_timer = 8
                    break
                elif active_pu == "shield":
                    active_pu = None
                    shake_timer = 8
                    obstacles.remove(ob)
                    break
                else:
                    return {"score": score, "distance": distance,
                            "coins": coin_score, "coin_count": coin_count}

        # Lane hazards
        for hz in hazards:
            if pr.colliderect(hz.get_rect()) and not hz.triggered:
                hz.triggered = True
                if hz.htype == "oil":
                    # Force lane swap
                    options = [l for l in range(3) if l != player.lane]
                    player.lane = random.choice(options)
                    player.x    = LANES[player.lane] - Car.W // 2
                    shake_timer = 12
                elif hz.htype == "slow":
                    slow_timer = 90   # ~1.5 s

        # Nitro strips
        for re in road_events:
            if isinstance(re, NitroStrip) and pr.colliderect(re.get_rect()):
                if not re.triggered:
                    re.triggered = True
                    score += 50   # bonus

        # Speed bumps
        for re in road_events:
            if isinstance(re, SpeedBump) and pr.colliderect(re.get_rect()):
                if not re.triggered:
                    re.triggered = True
                    shake_timer  = 18

        # Coins
        for c in coins:
            if pr.colliderect(c.get_rect()):
                c.collected   = True
                coin_score   += c.value
                coin_count   += 1
                score        += c.value * 2   # coin bonus to score
                if coin_count >= coins_to_next:
                    boost_level   += 1
                    coins_to_next += COINS_PER_BOOST

        # Power-ups
        for pu in powerups:
            if pr.colliderect(pu.get_rect()) and not pu.collected:
                pu.collected = True
                if pu.ptype == "nitro":
                    active_pu = "nitro"
                    pu_timer  = 4 * FPS        # 4 seconds
                elif pu.ptype == "shield":
                    active_pu = "shield"
                    pu_timer  = 0              # indefinite until hit
                elif pu.ptype == "repair":
                    active_pu = "repair"
                    pu_timer  = 1 * FPS        # 1-second window to use
                score += 100

        # ── Draw ─────────────────────────────────────────────────────────────
        draw_road(screen, stripe_offset, shake=shake_timer // 2)
        for hz in hazards:    hz.draw(screen)
        for re in road_events: re.draw(screen)
        for ob in obstacles:  ob.draw(screen)
        for e in enemies:     e.draw(screen)
        for c in coins:       c.draw(screen)
        for pu in powerups:   pu.draw(screen)
        player.draw(screen, shield=(active_pu == "shield"))
        draw_hud(screen, score, coin_score, boost_level,
                 coins_to_next - coin_count, distance,
                 active_pu, pu_timer)
        pygame.display.flip()
