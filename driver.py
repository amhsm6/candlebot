import time
import config

class Driver:
    def __init__(self, wheels, encoderl, encoderr):
        print('INIT driver', flush=True)

        self.wheels = wheels
        self.encoderl = encoderl
        self.encoderr = encoderr
        self.reset()

    def deinit(self):
        print('DEINIT driver', flush=True)

    def reset(self, preset=config.DRIVER_WALL_PARAMS, **kwargs):
        self.integral = 0
        self.control_prev = 0
        self.limcontrol_prev = 0
        self.err_prev = 0

        self.params = preset
        for p in kwargs:
            self.params[p] = kwargs[p]

    def iter(self, err):
        cp = err * self.params['kp']

        self.integral += err * self.params['dt'] * self.params['ki'] - (self.control_prev - self.limcontrol_prev) * self.params['kaw']

        cd = (err - self.err_prev) / self.params['dt'] * self.params['kd']

        control = cp + self.integral + cd
        self.control_prev = control

        control = min(control, self.params['max_control'])
        control = max(control, -self.params['max_control'])
        self.limcontrol_prev = control

        self.wheels.go(self.params['speed'] - control, self.params['speed'] + control)

        time.sleep(self.params['dt'])
        self.err_prev = err

    def fwd(self, v, cm):
        self.wheels.go(v, v)

        lref = self.encoderl.getValue()
        lval = lref

        rref = self.encoderr.getValue()
        rval = rref

        while abs(lval - lref) < config.cm_to_enc(cm) and abs(rval - rref) < config.cm_to_enc(cm):
            lval = self.encoderl.getValue()
            rval = self.encoderr.getValue()
            time.sleep(0.001)
        
        self.wheels.stop()

    def turn(self, v, deg):
        self.wheels.go(v, -v)

        lref = self.encoderl.getValue()
        lval = lref

        rref = self.encoderr.getValue()
        rval = rref

        while abs(lval - lref) < config.deg_to_enc(deg) and abs(rval - rref) < config.deg_to_enc(deg):
            lval = self.encoderl.getValue()
            rval = self.encoderr.getValue()
            time.sleep(0.001)
        
        self.wheels.stop()
