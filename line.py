import digitalio

class Line:
    def __init__(self):
        print('INIT line')

        self.line = digitalio.DigitalInOut(config.LINE_SENSOR)
        self.line.switch_to_input()

    def deinit(self):
        self.line.deinit()
    
    def check_room(self):
        # FIXME
        return self.line.value < 500
