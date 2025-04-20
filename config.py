import board

DRIVER_WALL_PARAMS = {
    'kp': 60,
    'ki': 20,
    'kaw': 0,
    'kd': 2.5,
    'speed': 15000,
    'dt': 0.01,
    'max_control': 40000
}

DRIVER_CANDLE_PARAMS = {
    'kp': 100,
    'ki': 0,
    'kaw': 0,
    'kd': 5,
    'speed': 6000,
    'dt': 0.01,
    'max_control': 40000
}

EYES_XSHUTS = [
    (board.D18, 0x28),
    (board.D6, 0x27),
    (board.D15, 0x26),
]

WHEELS_ENA = board.D26
WHEELS_IN1 = board.D19
WHEELS_IN2 = board.D13
WHEELS_IN3 = board.D20
WHEELS_IN4 = board.D16
WHEELS_ENB = board.D21

TURBINE_PIN = board.D4
TURBINE_OFF = 3000
TURBINE_ON = 4500

ENCODERL_PIN1 = 11
ENCODERL_PIN2 = 9

ENCODERR_PIN1 = 22
ENCODERR_PIN2 = 27

LINE_SENSOR = board.D25

WHEEL_BASE = 18
WHEEL_DIAM = 4.2

WHEEL_REV = 690

def deg_to_cm(deg):
    return (deg / 360.0) * 3.14 * WHEEL_BASE

def cm_to_enc(cm):
    return cm / (3.14 * WHEEL_DIAM) * WHEEL_REV
 
def deg_to_enc(deg):
    return cm_to_enc(deg_to_cm(deg))
