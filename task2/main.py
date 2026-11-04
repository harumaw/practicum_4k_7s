import sys

import pygame

import config as cfg
from astar import path_cost, search_steps
from grid import is_passable, load_map_from_file, random_map


def cell_color(passability):
    if passability <= 0.0:
        return (15, 15, 18)
    v = int(60 + 195 * passability)
    return (v, v, v)


class App:
    def __init__(self):
        pygame.init()
        self.grid = random_map()
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.width = self.cols * cfg.CELL_SIZE
        self.height = cfg.HUD_HEIGHT + self.rows * cfg.CELL_SIZE
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("A* — поиск пути на карте проходимости")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 16)

        self.start = None
        self.goal = None
        self.closed = set()
        self.path = None
        self.search_gen = None
        self.searching = False
        self.status = "ЛКМ — старт, ПКМ — финиш, ENTER — искать путь"

    def reset_search(self):
        self.closed = set()
        self.path = None
        self.search_gen = None
        self.searching = False

    def load_random_map(self):
        self.grid = random_map()
        self.reset_search()
        self.start = None
        self.goal = None
        self.status = "Сгенерирована случайная карта"

    def load_file_map(self):
        try:
            grid = load_map_from_file(cfg.DEFAULT_MAP_FILE)
        except OSError as e:
            self.status = f"Не удалось загрузить файл: {e}"
            return
        self.grid = grid
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.width = self.cols * cfg.CELL_SIZE
        self.height = cfg.HUD_HEIGHT + self.rows * cfg.CELL_SIZE
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.reset_search()
        self.start = None
        self.goal = None
        self.status = f"Загружена карта из {cfg.DEFAULT_MAP_FILE}"

    def cell_at(self, pos):
        x, y = pos
        if y < cfg.HUD_HEIGHT:
            return None
        col = x // cfg.CELL_SIZE
        row = (y - cfg.HUD_HEIGHT) // cfg.CELL_SIZE
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return (row, col)
        return None

    def start_search(self):
        if self.start is None or self.goal is None:
            self.status = "Сначала укажите старт (ЛКМ) и финиш (ПКМ)"
            return
        self.closed = set()
        self.path = None
        self.search_gen = search_steps(self.grid, self.start, self.goal, cfg.DIAGONAL_MOVEMENT)
        self.searching = True
        self.status = "Идёт поиск..."

    def advance_search(self):
        if not self.searching or self.search_gen is None:
            return
        for _ in range(cfg.EXPANSIONS_PER_FRAME):
            try:
                kind, payload = next(self.search_gen)
            except StopIteration:
                self.searching = False
                return
            if kind == "expand":
                self.closed.add(payload)
            else:  # "done"
                self.path = payload
                self.searching = False
                if self.path is None:
                    self.status = "Путь не найден"
                else:
                    cost = path_cost(self.grid, self.path)
                    self.status = f"Путь найден: {len(self.path)} клеток, стоимость={cost:.2f}"
                return

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_r:
                self.load_random_map()
            elif event.key == pygame.K_l:
                self.load_file_map()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_search()
            elif event.key == pygame.K_c:
                self.reset_search()
                self.status = "Визуализация поиска очищена"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            cell = self.cell_at(event.pos)
            if cell is not None and is_passable(self.grid, *cell):
                if event.button == 1:
                    self.start = cell
                    self.reset_search()
                    self.status = f"Старт: {cell}"
                elif event.button == 3:
                    self.goal = cell
                    self.reset_search()
                    self.status = f"Финиш: {cell}"
        return True

    def draw(self):
        self.screen.fill((25, 25, 30))

        for line_idx, line in enumerate([
            "ЛКМ — поставить старт   ПКМ — поставить финиш   ENTER/SPACE — искать путь",
            "R — случайная карта   L — загрузить карту из файла   C — очистить поиск   ESC — выход",
            self.status,
        ]):
            surf = self.font.render(line, True, (220, 220, 220))
            self.screen.blit(surf, (10, 8 + line_idx * 20))

        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(
                    c * cfg.CELL_SIZE, cfg.HUD_HEIGHT + r * cfg.CELL_SIZE,
                    cfg.CELL_SIZE, cfg.CELL_SIZE,
                )
                pygame.draw.rect(self.screen, cell_color(self.grid[r][c]), rect)

        if self.closed:
            overlay = pygame.Surface((cfg.CELL_SIZE, cfg.CELL_SIZE), pygame.SRCALPHA)
            overlay.fill((60, 140, 255, 90))
            for (r, c) in self.closed:
                self.screen.blit(overlay, (c * cfg.CELL_SIZE, cfg.HUD_HEIGHT + r * cfg.CELL_SIZE))

        if self.path:
            points = [
                (c * cfg.CELL_SIZE + cfg.CELL_SIZE // 2, cfg.HUD_HEIGHT + r * cfg.CELL_SIZE + cfg.CELL_SIZE // 2)
                for (r, c) in self.path
            ]
            if len(points) > 1:
                pygame.draw.lines(self.screen, (255, 200, 40), False, points, 4)
            for p in points:
                pygame.draw.circle(self.screen, (255, 200, 40), p, 3)

        for cell, color in ((self.start, (40, 200, 60)), (self.goal, (220, 50, 50))):
            if cell is not None:
                r, c = cell
                rect = pygame.Rect(
                    c * cfg.CELL_SIZE, cfg.HUD_HEIGHT + r * cfg.CELL_SIZE,
                    cfg.CELL_SIZE, cfg.CELL_SIZE,
                )
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, width=2)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                running = self.handle_event(event)
                if not running:
                    break

            self.advance_search()
            self.draw()
            self.clock.tick(cfg.FPS)

        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    App().run()
