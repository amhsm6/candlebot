import board
import math

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
    'ki': 8,
    'kaw': 0,
    'kd': 1.4,
    'speed': 18000,
    'dt': 0.01,
    'max_control': 50000
}

DRIVER_WALL_ONESIDE = {
    'kp': 30,
    'ki': 12,
    'kaw': 0,
    'kd': 3.2,
    'speed': 15000,
    'dt': 0.01,
    'max_control': 8000
}

DRIVER_CANDLE_PARAMS = {
    'kp': 200,
    'ki': 16,
    'kaw': 0,
    'kd': 11,
    'speed': 10000,
    'dt': None,
    'max_control': 15000
}

DRIVER_DEFAULT_PARAMS = DRIVER_WALL_PARAMS_BAT_FULL 

EYES_XSHUTS = [
    (board.D25, 0x28),
    (board.D1, 0x25),
    (board.D12, 0x26),
    (board.D8, 0x30),
    (board.D7, 0x24),
]

EYES_FILTER_WINDOW = 3

WHEELS_ENA = board.D0
WHEELS_IN1 = board.D6
WHEELS_IN2 = board.D5
WHEELS_IN3 = board.D13
WHEELS_IN4 = board.D19
WHEELS_ENB = board.D26

TURBINE_PIN = board.D21
TURBINE_OFF = 3000
TURBINE_ON = 4500

ENCODERL_PIN1 = 24
ENCODERL_PIN2 = 23

ENCODERR_PIN1 = 18
ENCODERR_PIN2 = 15

LINE_SENSOR = board.D16

BUTTON_PIN = board.D11

WHEEL_BASE = 15
WHEEL_DIAM = 4.2

WHEEL_REV = 690

def deg_to_cm(deg):
    return (deg / 360.0) * math.pi * WHEEL_BASE

def cm_to_enc(cm):
    return cm / (math.pi * WHEEL_DIAM) * WHEEL_REV

def enc_to_cm(enc):
    return enc * (math.pi * WHEEL_DIAM) / WHEEL_REV
 
def deg_to_enc(deg):
    return cm_to_enc(deg_to_cm(deg))
