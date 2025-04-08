import digitalio

class Line:
    def __init__(self):
        print('INIT line', flush=True)

        self.line = digitalio.DigitalInOut(config.LINE_SENSOR)
        self.line.switch_to_input()

    def deinit(self):
        print('DEINIT line', flush=True)
        self.line.deinit()
    
    def check_room(self):
        # FIXME
        return self.line.value < 500
