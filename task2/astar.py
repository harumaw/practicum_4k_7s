
import heapq
import itertools
import math

from grid import is_passable

_SQRT2 = math.sqrt(2)

_NEIGHBORS_8 = [
    (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
    (-1, -1, _SQRT2), (-1, 1, _SQRT2), (1, -1, _SQRT2), (1, 1, _SQRT2),
]
_NEIGHBORS_4 = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0)]


def cell_cost(passability):
    return 1.0 / passability


def octile_heuristic(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return (dx + dy) + (_SQRT2 - 2) * min(dx, dy)


def manhattan_heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def search_steps(grid, start, goal, diagonal=True):
    neighbors = _NEIGHBORS_8 if diagonal else _NEIGHBORS_4
    heuristic = octile_heuristic if diagonal else manhattan_heuristic

    if not is_passable(grid, *start) or not is_passable(grid, *goal):
        yield ("done", None)
        return

    counter = itertools.count()
    open_heap = [(heuristic(start, goal), next(counter), start)]
    g_score = {start: 0.0}
    came_from = {}
    closed = set()

    while open_heap:
        _f, _, current = heapq.heappop(open_heap)
        if current in closed:
            continue
        closed.add(current)
        yield ("expand", current)

        if current == goal:
            yield ("done", _reconstruct_path(came_from, current))
            return

        for dr, dc, mult in neighbors:
            nr, nc = current[0] + dr, current[1] + dc
            neighbor = (nr, nc)
            if neighbor in closed or not is_passable(grid, nr, nc):
                continue

            tentative_g = g_score[current] + mult * cell_cost(grid[nr][nc])
            if tentative_g < g_score.get(neighbor, math.inf):
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_heap, (f_score, next(counter), neighbor))

    yield ("done", None)


def find_path(grid, start, goal, diagonal=True):
    closed = set()
    for kind, payload in search_steps(grid, start, goal, diagonal):
        if kind == "expand":
            closed.add(payload)
        else:
            return payload, closed
    return None, closed


def path_cost(grid, path):
    if not path:
        return 0.0
    total = 0.0
    for (r0, c0), (r1, c1) in zip(path, path[1:]):
        mult = _SQRT2 if (r0 != r1 and c0 != c1) else 1.0
        total += mult * cell_cost(grid[r1][c1])
    return total
