import board
import pwmio
import config
import time

class Turbine():
    def __init__(self):
        print('INIT turbine')
        self.pwm = pwmio.PWMOut(config.TURBINE_PIN, frequency=50)
        self.off()

    def deinit(self):
        print('DEINIT turbine')
        self.off()
        self.pwm.deinit()

    def set(self, x):
        self.pwm.duty_cycle = x

    def off(self):
        self.set(config.TURBINE_OFF)

    def on(self):
        self.set(config.TURBINE_ON)
