import board
import time

from camera import Camera
from eyes import Eyes
from wheels import Wheels

i2c = board.I2C()
camera = Camera()
eyes = Eyes(i2c)
wheels = Wheels()

KP = 40
KD = 0
SPEED = 20000

try:
    while True:
        #dist = eyes.see(0)
        #err = dist - 200

        #power = err * KP
        #print(dist)
        #print(SPEED + power, SPEED - power)

        #wheels.go(SPEED + power, SPEED - power)

        im = camera.read()
        for row in range(24):
            for col in range(32):
                print(f'{im[row, col]:.2f}', end=' ')

            print()

        print('=' * 15)
        time.sleep(1)

except KeyboardInterrupt:
    print()

camera.deinit()
eyes.deinit()
wheels.deinit()
