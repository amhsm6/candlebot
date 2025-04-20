import board
from digitalio import DigitalInOut
from adafruit_vl53l0x import VL53L0X
import time
import config

class Eyes():
    def __init__(self, i2c):
        print('INIT eyes', flush=True)

        def init_xshut(x):
            pin = x[0]
            addr = x[1]

            xshut = DigitalInOut(pin)
            xshut.switch_to_output(value=False)

            return (xshut, addr)

        self.xshuts = list(map(init_xshut, config.EYES_XSHUTS))
        time.sleep(0.1)

        self.eyes = []
        for xshut, addr in self.xshuts:
            xshut.value = True
            time.sleep(0.1)

            print(f'TRY eyes on 0x{addr:x}...', flush=True)
            eye = VL53L0X(i2c)
            eye.set_address(addr)
            eye.start_continuous()

            self.eyes.append(eye)

            print(f'SUCCESS eyes on 0x{addr:x}', flush=True)

    def deinit(self):
        print('DEINIT eyes', flush=True)

        try:
            for xshut, _ in self.xshuts:
                xshut.deinit()

            for eye in self.eyes:
                eye.stop_continuous()

        except OSError as e:
            print('FAILURE eyes', flush=True)

    def see(self, n=None):
        def see_eye(x):
            (n, eye) = x

            try:
                return eye.range
            except OSError as e:
                print(f'FAILURE eye {n}', flush=True)
                return None

        if n == None:
            return list(map(see_eye, enumerate(self.eyes)))

        return see_eye((n, self.eyes[n]))
