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

    def see(self, sensors=None):
        if sensors is None:
            sensors = [i for i in range(len(self.eyes))]

        def see_eye(n):
            try:
                return self.eyes[n].range
            except OSError as e:
                print(f'FAILURE eye {n}', flush=True)
                return None

        measurements = [[] for _ in range(len(sensors))]

        for _ in range(config.EYES_FILTER_WINDOW):
            for i, measure in enumerate(map(see_eye, sensors))
                measurements[i].append(measure)

            time.sleep(0.001)
        
        return list(map(lambda data: sorted(data)[config.EYES_FILTER_WINDOW // 2], measurements))
