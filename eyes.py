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
            time.sleep(0.2)

            print(f'TRY eyes on 0x{addr:x}...', flush=True)
            eye = VL53L0X(i2c)
            eye.set_address(addr)
            eye.start_continuous()

            self.eyes.append(eye)

            print(f'SUCCESS eyes on 0x{addr:x}', flush=True)

    def deinit(self):
        print('DEINIT eyes', flush=True)

        try:
            for eye in self.eyes:
                eye.stop_continuous()

            for xshut, _ in self.xshuts:
                xshut.deinit()

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

        measurements = None
        if n is None:
            measurements = [[] for _ in range(len(self.eyes))]
        else:
            measurements = [[]]

        for _ in range(config.EYES_FILTER_WINDOW):
            if n is None:
                for i, measure in enumerate(map(see_eye, enumerate(self.eyes))):
                    measurements[i].append(measure)
            else:
                measurements[0].append(see_eye((n, self.eyes[n])))

            time.sleep(0.001)
        
        res = list(map(lambda data: sorted(data)[config.EYES_FILTER_WINDOW // 2], measurements))
        if n is None:
            return res
        else:
            return res[0]
