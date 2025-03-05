import board
import digitalio
import pwmio
import time

class Wheels():
    def __init__(self):
        print('INIT wheels')

        self.ena = pwmio.PWMOut(board.D13)
        self.in1 = digitalio.DigitalInOut(board.D19)
        self.in2 = digitalio.DigitalInOut(board.D26)
        self.in3 = digitalio.DigitalInOut(board.D16)
        self.in4 = digitalio.DigitalInOut(board.D20)
        self.enb = pwmio.PWMOut(board.D12)

        self.in1.switch_to_output(value=False)
        self.in2.switch_to_output(value=False)
        self.in3.switch_to_output(value=False)
        self.in4.switch_to_output(value=False)

    def deinit(self):
        print('DEINIT wheels')

        self.stop()

        self.ena.deinit()
        self.in1.deinit()
        self.in2.deinit()
        self.in3.deinit()
        self.in4.deinit()
        self.enb.deinit()

    def go(self, vl, vr):
        dirl = vl / abs(vl) if vl != 0 else 0
        dirr = vr / abs(vr) if vr != 0 else 0

        self.in1.value = dirl < 0
        self.in2.value = dirl > 0

        self.in3.value = dirr > 0
        self.in4.value = dirr < 0

        vl = min(abs(vl), 65535)
        vr = min(abs(vr), 65535)

        self.ena.duty_cycle = vl
        self.enb.duty_cycle = vr

    def stop(self):
        self.in1.value = True
        self.in2.value = True
        self.in3.value = True
        self.in4.value = True
        self.ena.duty_cycle = 65535
        self.enb.duty_cycle = 65535
        time.sleep(0.1)

        self.go(0, 0)
