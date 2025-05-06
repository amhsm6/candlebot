from digitalio import DigitalInOut, Pull
import config

class Button:
    def __init__(self):
        print('INIT button', flush=True)

        self.btn = DigitalInOut(config.BUTTON_PIN)
        self.btn.switch_to_input(Pull.DOWN)

    def deinit(self):
        print('DEINIT button', flush=True)
        self.btn.deinit()
    
    def pressed(self):
        return self.btn.value
