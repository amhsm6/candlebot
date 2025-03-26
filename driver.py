import time
import config

class Driver:
    def __init__(self, wheels, eyes):
        print('INIT driver')
        self.wheels = wheels
        self.eyes = eyes
        self.reset()

    def deinit(self):
        print('DEINIT driver')

    def reset(self):
        self.integral = 0
        self.control_prev = 0
        self.limcontrol_prev = 0
        self.err_prev = 0

    def iter(self):
        err = self.eyes.see(1) - self.eyes.see(0)

        cp = err * config.DRIVER_KP

        self.integral += err * config.DRIVER_DT * config.DRIVER_KI - (self.control_prev - self.limcontrol_prev) * config.DRIVER_KAW

        cd = (err - self.err_prev) / config.DRIVER_DT * config.DRIVER_KD

        control = cp + self.integral + cd
        self.control_prev = control

        control = min(control, config.DRIVER_MAX_CONTROL)
        control = max(control, -config.DRIVER_MAX_CONTROL)
        self.limcontrol_prev = control

        self.wheels.go(config.DRIVER_SPEED + control, config.DRIVER_SPEED - control)

        time.sleep(config.DRIVER_DT)
        self.err_prev = err
