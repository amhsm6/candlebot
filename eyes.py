import board
from digitalio import DigitalInOut
from adafruit_vl53l0x import VL53L0X
import time
import config

class Eyes():
    def __init__(self, i2c):
        print('INIT eyes')

        def init_xshut(x):
            pin = x[0]
            addr = x[1]

            xshut = DigitalInOut(pin)
            xshut.switch_to_output(value=False)

            return (xshut, addr)

        self.xshuts = map(init_xshut, config.EYES_XSHUTS)

        self.eyes = []
        for xshut, addr in self.xshuts:
            xshut.value = True
            time.sleep(0.1)

            eye = VL53L0X(i2c)
            eye.set_address(addr)
            eye.start_continuous()

            self.eyes.append(eye)

            print(f'INIT eyes success on 0x{addr:x}')

    def deinit(self):
        print('DEINIT eyes')

        for xshut, _ in self.xshuts:
            xshut.deinit()

        for eye in self.eyes:
            eye.stop_continuous()

    def see(self, n=None):
        if n == None:
            return list(map(lambda eye: eye.range, self.eyes))

        return self.eyes[n].range
