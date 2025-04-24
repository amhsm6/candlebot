import board

DRIVER_WALL_PARAMS_BAT_LOW = {
    'kp': 12,
    'ki': 3,
    'kaw': 0,
    'kd': 2,
    'speed': 20000,
    'dt': 0.01,
    'max_control': 50000
}

DRIVER_WALL_PARAMS_BAT_FULL = {
    'kp': 12,
    'ki': 3,
    'kaw': 0,
    'kd': 1,
    'speed': 15000,
    'dt': 0.01,
    'max_control': 50000
}

DRIVER_CANDLE_PARAMS = {
    'kp': 250,
    'ki': 10,
    'kaw': 0,
    'kd': 10,
    'speed': 12000,
    'dt': None,
    'max_control': 5000
}

DRIVER_DEFAULT_PARAMS = DRIVER_WALL_PARAMS_BAT_FULL 

EYES_XSHUTS = [
    (board.D5, 0x28),
    (board.D0, 0x25),
    (board.D6, 0x26),
    (board.D24, 0x30),
    (board.D23, 0x24),
]

EYES_FILTER_WINDOW = 3

WHEELS_ENA = board.D26
WHEELS_IN1 = board.D19
WHEELS_IN2 = board.D13
WHEELS_IN3 = board.D20
WHEELS_IN4 = board.D16
WHEELS_ENB = board.D21

TURBINE_PIN = board.D7
TURBINE_OFF = 3000
TURBINE_ON = 4500

ENCODERL_PIN1 = 11
ENCODERL_PIN2 = 9

ENCODERR_PIN1 = 22
ENCODERR_PIN2 = 27

LINE_SENSOR = board.D18

WHEEL_BASE = 16
WHEEL_DIAM = 4.2

WHEEL_REV = 690

def deg_to_cm(deg):
    return (deg / 360.0) * 3.14 * WHEEL_BASE

def cm_to_enc(cm):
    return cm / (3.14 * WHEEL_DIAM) * WHEEL_REV
 
def deg_to_enc(deg):
    return cm_to_enc(deg_to_cm(deg))
