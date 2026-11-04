import itertools

import config as cfg

_id_counter = itertools.count(1)


class Car:
    def __init__(self, desired_speed):
        self.id = next(_id_counter)
        self.position = 0.0
        self.desired_speed = desired_speed
        self.speed = desired_speed
        self.length = cfg.CAR_LENGTH
        self.forced_brake_until = None

    def is_jammed(self):
        return self.forced_brake_until is not None

    def start_forced_brake(self, now):
        self.forced_brake_until = now + cfg.FORCED_BRAKE_DURATION

    def update(self, dt, now, gap, leader_speed):
        if self.forced_brake_until is not None:
            if now < self.forced_brake_until:
                self.speed = max(0.0, self.speed - cfg.FORCED_BRAKE_DECEL * dt)
                self.position += self.speed * dt
                return
            self.forced_brake_until = None

        if gap is not None and gap < cfg.GAP_MIN:
            if self.speed > leader_speed:
                self.speed = max(leader_speed, self.speed - cfg.BRAKE * dt)
        elif gap is None or gap > cfg.GAP_MAX:
            if self.speed < self.desired_speed:
                self.speed = min(self.desired_speed, self.speed + cfg.ACCEL * dt)

        self.speed = max(0.0, self.speed)
        self.position += self.speed * dt
