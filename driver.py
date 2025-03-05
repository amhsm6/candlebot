import time

class Driver:
    KP = 120
    KI = 0
    KAW = 0
    KD = 0
    SPEED = 30000
    DT = 0.01
    MAX_CONTROL = 30000

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

        cp = err * Driver.KP

        self.integral += err * Driver.DT * Driver.KI - (self.control_prev - self.limcontrol_prev) * Driver.KAW

        cd = (err - self.err_prev) / Driver.DT * Driver.KD

        control = cp + self.integral + cd
        self.control_prev = control

        control = min(control, Driver.MAX_CONTROL)
        control = max(control, -Driver.MAX_CONTROL)
        self.limcontrol_prev = control

        print(self.eyes.see(), control, Driver.SPEED + control, Driver.SPEED - control)

        self.wheels.go(Driver.SPEED + control, Driver.SPEED - control)

        time.sleep(Driver.DT)
        self.err_prev = err
