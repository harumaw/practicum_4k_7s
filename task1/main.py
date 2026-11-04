import sys

import pygame

import config as cfg
from simulation import Simulation


def speed_to_color(speed, max_speed):
    t = max(0.0, min(1.0, speed / max_speed))
    r = int(220 * (1 - t) + 30 * t)
    g = int(30 * (1 - t) + 200 * t)
    b = 40
    return (r, g, b)


def road_y():
    return cfg.WINDOW_HEIGHT // 2


def to_px(x):
    return cfg.ROAD_MARGIN_X + x * cfg.PIXELS_PER_METER


def draw(screen, font, sim, jammed_flash, selected_car):
    screen.fill((25, 25, 30))

    y = road_y()
    pygame.draw.line(
        screen, (90, 90, 100),
        (cfg.ROAD_MARGIN_X, y), (cfg.WINDOW_WIDTH - cfg.ROAD_MARGIN_X, y), 3
    )
    lo = to_px(cfg.JAM_ZONE[0] * cfg.ROAD_LENGTH)
    hi = to_px(cfg.JAM_ZONE[1] * cfg.ROAD_LENGTH)
    zone_surf = pygame.Surface((hi - lo, 40), pygame.SRCALPHA)
    zone_surf.fill((255, 255, 0, 25))
    screen.blit(zone_surf, (lo, y - 20))

    car_rects = []
    for car in sim.cars:
        x = to_px(car.position)
        w = max(3, car.length * cfg.PIXELS_PER_METER)
        color = (255, 60, 60) if car.is_jammed() else speed_to_color(car.speed, cfg.SPEED_MAX)
        rect = pygame.Rect(0, 0, w, cfg.CAR_PIXEL_HEIGHT)
        rect.center = (x, y)
        pygame.draw.rect(screen, color, rect, border_radius=3)
        car_rects.append((car, rect))

        if car is selected_car:
            pygame.draw.rect(screen, (255, 255, 255), rect.inflate(4, 4), width=2, border_radius=4)

    hud_lines = [
        f"t = {sim.time:6.1f} c   машин на дороге: {len(sim.cars):3d}   уехало: {sim.removed_count}",
        f"средняя скорость: {sim.average_speed():5.1f} м/с",
        "SPACE — резко затормозить случайную машину в жёлтой зоне (пробка)   ЛКМ по машине — её скорость",
    ]
    for i, line in enumerate(hud_lines):
        surf = font.render(line, True, (220, 220, 220))
        screen.blit(surf, (cfg.ROAD_MARGIN_X, 20 + i * 22))

    if jammed_flash > 0:
        msg = font.render("Машина резко затормозила!", True, (255, 210, 60))
        screen.blit(msg, (cfg.WINDOW_WIDTH // 2 - 110, cfg.WINDOW_HEIGHT - 40))

    if selected_car is not None and selected_car in sim.cars:
        rect = dict(car_rects)[selected_car]
        label = f"v = {selected_car.speed:4.1f} м/с ({selected_car.speed * 3.6:5.1f} км/ч)"
        surf = font.render(label, True, (10, 10, 10))
        box = surf.get_rect()
        box.midbottom = (rect.centerx, rect.top - 6)
        box.left = max(4, min(box.left, cfg.WINDOW_WIDTH - box.width - 4))
        bg = box.inflate(10, 6)
        pygame.draw.rect(screen, (255, 255, 255), bg, border_radius=5)
        pygame.draw.rect(screen, (30, 30, 30), bg, width=1, border_radius=5)
        screen.blit(surf, box)

    return car_rects


def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
    pygame.display.set_caption("----")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 16)

    sim = Simulation()
    jammed_flash = 0
    car_rects = []
    selected_car = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if sim.trigger_jam() is not None:
                        jammed_flash = 90
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                selected_car = None
                for car, rect in reversed(car_rects):
                    if rect.inflate(6, 10).collidepoint(event.pos):
                        selected_car = car
                        break

        sim.step(cfg.DT)
        jammed_flash = max(0, jammed_flash - 1)

        if selected_car not in sim.cars:
            selected_car = None

        car_rects = draw(screen, font, sim, jammed_flash, selected_car)
        pygame.display.flip()
        clock.tick(cfg.FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
