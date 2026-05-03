"""
persistence.py
Handles saving and loading leaderboard entries and game settings to/from JSON files.
"""

import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

# ── Default settings ──────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    "sound":      False,          # sound toggle (no audio assets, but flag is saved)
    "car_color":  "blue",         # "blue" | "red" | "green" | "yellow" | "purple"
    "difficulty": "normal",       # "easy" | "normal" | "hard"
}


# ── Settings ──────────────────────────────────────────────────────────────────

def load_settings() -> dict:
    """Return saved settings, falling back to defaults for missing keys."""
    settings = dict(DEFAULT_SETTINGS)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                saved = json.load(f)
            for k, v in saved.items():
                if k in settings:
                    settings[k] = v
        except (json.JSONDecodeError, OSError):
            pass
    return settings


def save_settings(settings: dict) -> None:
    """Persist the settings dict to disk."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except OSError:
        pass


# ── Leaderboard ───────────────────────────────────────────────────────────────

def load_leaderboard() -> list:
    """Return a list of entry dicts: {name, score, distance, coins}."""
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return []


def save_leaderboard(entries: list) -> None:
    """Write the full leaderboard list to disk."""
    try:
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(entries, f, indent=2)
    except OSError:
        pass


def add_leaderboard_entry(name: str, score: int, distance: int, coins: int) -> list:
    """
    Insert a new entry, keep only the top 10 by score, and persist.
    Returns the updated leaderboard.
    """
    entries = load_leaderboard()
    entries.append({"name": name, "score": score,
                    "distance": distance, "coins": coins})
    entries.sort(key=lambda e: e["score"], reverse=True)
    entries = entries[:10]
    save_leaderboard(entries)
    return entries
