
ROAD_LENGTH = 2500.0        # длина участка дороги


SPAWN_RATE = 0.35           # интенсивность потока (машин/сек), 


SPEED_DISTRIBUTION = "gaussian" # "gaussian" или "uniform"
SPEED_MEAN = 20.0           # м/с, для gaussian (+-72 км/ч)
SPEED_STD = 4.0             # м/с, для gaussian
SPEED_MIN = 10.0            # м/с, нижняя граница (для uniform и обрезки gaussian)
SPEED_MAX = 28.0            # м/с, верхняя граница (для uniform и обрезки gaussian)

# логика следования за лидером
GAP_MIN = 18.0              # м, если дистанция меньше - тормозим
GAP_MAX = 45.0              # м, если дистанция больше - разгоняемся до желаемой скорости
ACCEL = 2.0                 # м/с^2, ускорение разгона
BRAKE = 3.0                 # м/с^2, замедление при приближении к лидеру

CAR_LENGTH = 4.5            # м, длина машинки (для расчёта зазора)

# резкое торможение (принудитеельноне) (клавиша SPACE) 
FORCED_BRAKE_DURATION = 4.0     # сек, как долго машина тормозит принудительно
FORCED_BRAKE_DECEL = 7.0        # м/с^2, экстренное торможение
JAM_ZONE = (0.4, 0.6)           # доля длины дороги, из которой выбирается машина для торможения

# simulation
DT = 1.0 / 60.0             # шаг времени, сек
FPS = 60

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 420
ROAD_MARGIN_X = 40
PIXELS_PER_METER = (WINDOW_WIDTH - 2 * ROAD_MARGIN_X) / ROAD_LENGTH
CAR_PIXEL_HEIGHT = 16
