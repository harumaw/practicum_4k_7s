import random

import config as cfg
from car import Car


def sample_speed():
    if cfg.SPEED_DISTRIBUTION == "gaussian":
        v = random.gauss(cfg.SPEED_MEAN, cfg.SPEED_STD)
    else:
        v = random.uniform(cfg.SPEED_MIN, cfg.SPEED_MAX)
    return min(max(v, cfg.SPEED_MIN), cfg.SPEED_MAX)


class Simulation:
    """
    Хранит машинки на дороге в порядке от переднего к заднему
    (cars[0] — самая дальняя от старта, cars[-1] — ближайшая к старту).
    Обгон невозможен, поэтому этот порядок не меняется со временем.
    """

    def __init__(self):
        self.cars = []
        self.time = 0.0
        self.next_spawn_time = random.expovariate(cfg.SPAWN_RATE)
        self.removed_count = 0

    def _try_spawn(self):
        if self.time < self.next_spawn_time:
            return
        # место для новой машинки в начале дороги
        if self.cars:
            last = self.cars[-1]
            if last.position - last.length < cfg.CAR_LENGTH:
                return  # пока нет места — попробуем на следующем шаге
        car = Car(desired_speed=sample_speed())
        self.cars.append(car)
        self.next_spawn_time = self.time + random.expovariate(cfg.SPAWN_RATE)

    def trigger_jam(self):
        """Выбрать случайную машину в средней зоне дороги и резко её затормозить."""
        lo = cfg.JAM_ZONE[0] * cfg.ROAD_LENGTH
        hi = cfg.JAM_ZONE[1] * cfg.ROAD_LENGTH
        candidates = [c for c in self.cars if lo <= c.position <= hi and not c.is_jammed()]
        if not candidates:
            return None
        car = random.choice(candidates)
        car.start_forced_brake(self.time)
        return car

    def step(self, dt):
        self.time += dt
        self._try_spawn()

        # снимок состояния до обновления, чтобы все машины считали зазор
        # относительно позиций/скоростей текущего кадра
        snapshot = [(c.position, c.speed) for c in self.cars]

        for i, car in enumerate(self.cars):
            if i == 0:
                gap = None
                leader_speed = None
            else:
                leader_pos, leader_speed = snapshot[i - 1]
                leader_len = self.cars[i - 1].length
                gap = leader_pos - leader_len - snapshot[i][0]
            car.update(dt, self.time, gap, leader_speed)

        # защита от наезда (численная погрешность): не даём заднему бамперу
        # обогнать лидера
        for i in range(1, len(self.cars)):
            leader = self.cars[i - 1]
            follower = self.cars[i]
            max_pos = leader.position - leader.length
            if follower.position > max_pos:
                follower.position = max_pos
                follower.speed = min(follower.speed, leader.speed)

        # удаляем машины, доехавшие до конца дороги
        before = len(self.cars)
        self.cars = [c for c in self.cars if c.position < cfg.ROAD_LENGTH]
        self.removed_count += before - len(self.cars)

    def average_speed(self):
        if not self.cars:
            return 0.0
        return sum(c.speed for c in self.cars) / len(self.cars)
