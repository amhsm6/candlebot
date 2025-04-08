import digitalio
import config

class Encoders:
    def __init__(self):
        print('INIT encoders', flush=True)

        self.left_pin1 = digitalio.DigitalInOut(config.ENCODERL_PIN1)
        self.left_pin2 = digitalio.DigitalInOut(config.ENCODERL_PIN2)
        self.left_pin1.switch_to_input()
        self.left_pin2.switch_to_input()

        self.right_pin1 = digitalio.DigitalInOut(config.ENCODERR_PIN1)
        self.right_pin2 = digitalio.DigitalInOut(config.ENCODERR_PIN2)
        self.right_pin1.switch_to_input()
        self.right_pin2.switch_to_input()

        self.reset()

    def deinit(self):
        print('DEINIT encoders', flush=True)

        self.left_pin1.deinit()
        self.left_pin2.deinit()
        self.right_pin1.deinit()
        self.right_pin2.deinit()

    def reset(self):
        self.left_pin1_prev = 0
        self.right_pin1_prev = 0

        self.left = 0
        self.right = 0

    def iter(self):
        if self.left_pin1.value and not self.left_pin1_prev:
            if self.left_pin1.value > self.left_pin2.value:
                self.left -= 1
            else:
                self.left += 1

        self.left_pin1_prev = self.left_pin1.value

        if self.right_pin1.value and not self.right_pin1_prev:
            if self.right_pin1.value > self.right_pin2.value:
                self.right -= 1
            else:
                self.right += 1

        self.right_pin1_prev = self.right_pin1.value
