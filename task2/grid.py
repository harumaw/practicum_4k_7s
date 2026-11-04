
import random

import config as cfg


def load_map_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        raw_lines = [line.rstrip("\n").rstrip("\r") for line in f]
    raw_lines = [line for line in raw_lines if line != ""] or [" "]
    width = max(len(line) for line in raw_lines)

    grid = []
    for line in raw_lines:
        line = line.ljust(width, " ")
        row = [char_to_passability(ch) for ch in line]
        grid.append(row)
    return grid


def char_to_passability(ch):
    if ch == " ":
        return 1.0
    if ch.isdigit():
        return int(ch) / 10.0
    return 0.0


def random_map(rows=cfg.RANDOM_ROWS, cols=cfg.RANDOM_COLS, rng=None):
    rng = rng or random
    grid = []
    for _r in range(rows):
        row = []
        for _c in range(cols):
            roll = rng.random()
            if roll < cfg.WALL_PROBABILITY:
                row.append(0.0)
            elif roll < cfg.WALL_PROBABILITY + cfg.ROUGH_PROBABILITY:
                row.append(rng.randint(1, 9) / 10.0)
            else:
                row.append(1.0)
        grid.append(row)
    return grid


def in_bounds(grid, r, c):
    return 0 <= r < len(grid) and 0 <= c < len(grid[0])


def is_passable(grid, r, c):
    return in_bounds(grid, r, c) and grid[r][c] > 0.0
