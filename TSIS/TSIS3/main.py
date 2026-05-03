"""
main.py
Entry point for the extended Racer game (SIS 3).

Screen flow:
  Main Menu → (username entry) → Gameplay → Game Over → Main Menu / Retry
           ↘ Leaderboard
           ↘ Settings
"""

import pygame
import sys

from persistence import load_settings, add_leaderboard_entry
from ui          import (screen_main_menu, screen_username, screen_settings,
                          screen_leaderboard, screen_game_over)
from racer       import game as run_race


def main():
    pygame.init()
    WIDTH, HEIGHT = 500, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Racer — Advanced Edition")
    clock  = pygame.time.Clock()

    # Load persisted settings once at startup
    settings    = load_settings()
    player_name = None   # asked once per session (or each new run)

    while True:
        action = screen_main_menu(screen, clock)

        if action == "quit":
            pygame.quit()
            sys.exit()

        elif action == "leaderboard":
            screen_leaderboard(screen, clock)

        elif action == "settings":
            settings = screen_settings(screen, clock)

        elif action == "play":
            # Ask for name if we don't have one yet
            if player_name is None:
                player_name = screen_username(screen, clock)

            retry = True
            while retry:
                result = run_race(screen, clock, settings, player_name)

                # Persist score
                add_leaderboard_entry(
                    player_name,
                    result["score"],
                    result["distance"],
                    result["coins"],
                )

                go_action = screen_game_over(
                    screen, clock,
                    result["score"],
                    result["distance"],
                    result["coins"],
                )
                retry = (go_action == "retry")
                if go_action == "menu":
                    break


if __name__ == "__main__":
    main()
