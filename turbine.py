import board
import pwmio

class Turbine():
    def __init__(self):
        print('INIT turbine')
        self.pwm = pwmio.PWMOut(board.D15, frequency=50)

    def deinit(self):
        print('DEINIT turbine')
        self.set(0)
        self.pwm.deinit()

    def set(self, x):
        self.pwm.duty_cycle = x

    def off(self):
        self.set(3000)

    def on(self):
        self.set(8000)
