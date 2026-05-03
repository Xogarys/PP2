# TSIS3 — Racer: Advanced Edition

An extended lane-based racing game built with **Pygame**, adding everything
required by SIS 3 on top of the Practice 10–11 base.

## Quick Start

```bash
pip install pygame
python main.py
```

## File Overview

| File | Purpose |
|---|---|
| `main.py` | Entry point; screen-flow orchestrator |
| `racer.py` | Core gameplay loop, all game objects |
| `ui.py` | All non-gameplay screens (menu, settings, leaderboard, game-over, name entry) |
| `persistence.py` | JSON save/load for leaderboard and settings |
| `settings.json` | Persisted player preferences (auto-created) |
| `leaderboard.json` | Top-10 scores (auto-created) |
| `assets/` | Placeholder for future images / sounds |

## Controls

| Key | Action |
|---|---|
| ← / A | Move left |
| → / D | Move right |
| R | Retry (Game Over screen) |
| M | Main Menu (Game Over screen) |

## Features Added (SIS 3)

### Gameplay & Track
- **Oil spills** – force a random lane swap on contact
- **Mud zones** – halve road speed for ~1.5 s
- **Nitro strips** – full-width glowing bar; touching gives a score bonus
- **Moving barriers** – laterally sliding obstacles that must be dodged
- **Speed bumps** – shake the camera on contact
- **Potholes** – instant game-over hazards (avoidable with Shield or Repair)

### Traffic & Obstacles
- Enemy cars spawn more frequently and faster as distance increases
- Safe-spawn logic prevents enemies from appearing on top of the player
- Difficulty multiplier scales traffic density and hazard frequency

### Power-Ups (one active at a time, disappear if uncollected)
| Power-up | Effect | Duration |
|---|---|---|
| **Nitro** (N) | 1.6× road speed | 4 seconds |
| **Shield** (S) | Absorbs one collision | Until hit |
| **Repair** (R) | Clears one pothole / collision | 1-second window |

### Scoring
- Distance score: 1 point per frame
- Coins: 1 / 3 / 5 points (Bronze / Silver / Gold) + ×2 bonus to total score
- Nitro strip touch: +50 points
- Power-up collect: +100 points

### Screens
- **Main Menu** — Play, Leaderboard, Settings, Quit (mouse buttons)
- **Username Entry** — typed name stored for the session
- **Settings** — sound toggle, car color (5 options), difficulty (Easy / Normal / Hard); saved to `settings.json`
- **Leaderboard** — top 10 by score with name, score, distance, coins; saved to `leaderboard.json`
- **Game Over** — shows score, distance, coins; Retry or Main Menu buttons
