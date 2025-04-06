import board

DRIVER_WALL_PARAMS = {
    'kp': 120,
    'ki': 0,
    'kaw': 0,
    'kd': 0,
    'speed': 30000,
    'dt': 0.01,
    'max_control': 30000
}

DRIVER_CANDLE_PARAMS = {
    'kp': 100,
    'ki': 0,
    'kaw': 0,
    'kd': 5,
    'speed': 6000,
    'dt': 0.01,
    'max_control': 15000
}

EYES_XSHUTS = [
    (board.D27, 0x28),
    (board.D17, 0x29)
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
