import board
import time

from camera import Camera
from eyes import Eyes
from wheels import Wheels

i2c = board.I2C()
camera = Camera()
eyes = Eyes(i2c)
wheels = Wheels()

KP = 35
KI = 5
KD = 13
SPEED = 20000
DT = 0.01

try:
    err_old = 0
    err_sum = 0
    while True:
        dist = eyes.see(0)
        err = dist - 150

        err_sum += err
        control = err * KP + err_sum * DT * KI + (err - err_old) / DT * KD
        err_old = err

        wheels.go(SPEED + control, SPEED - control)
        time.sleep(DT)

        #im = camera.read()
        #for row in range(24):
        #    for col in range(32):
        #        print(f'{im[row, col]:.2f}', end=' ')

        #    print()

        #print('=' * 15)

except KeyboardInterrupt:
    print()

camera.deinit()
eyes.deinit()
wheels.deinit()
