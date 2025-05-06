import time
import config

class Driver:
    def __init__(self, wheels, encoderl, encoderr, gyro):
        print('INIT driver', flush=True)

        self.wheels = wheels
        self.encoderl = encoderl
        self.encoderr = encoderr
        self.gyro = gyro
        self.reset()

    def deinit(self):
        print('DEINIT driver', flush=True)

    def reset(self, preset=config.DRIVER_DEFAULT_PARAMS, **kwargs):
        self.integral = 0
        self.control_prev = 0
        self.limcontrol_prev = 0
        self.err_prev = 0

        self.params = {}

        for p in preset:
            self.params[p] = preset[p]

        for p in kwargs:
            self.params[p] = kwargs[p]

        self.lref = self.encoderl.getValue()
        self.rref = self.encoderr.getValue()

        self.gyro.reset()
        self.angleref = self.gyro.get_angle()

    def iter(self, err):
        dt = self.params['dt'] if self.params['dt'] is not None else 1

        cp = err * self.params['kp']

        self.integral += err * dt * self.params['ki']

        cd = (err - self.err_prev) / dt * self.params['kd']

        control = cp + self.integral + cd
        self.control_prev = control

        control = min(control, self.params['max_control'])
        control = max(control, -self.params['max_control'])
        self.limcontrol_prev = control
    
        self.wheels.go(self.params['speed'] - control, self.params['speed'] + control)

        if self.params['dt'] is not None:
            time.sleep(dt)

        self.err_prev = err

    def encl(self):
        return abs(self.encoderl.getValue() - self.lref)

    def encr(self):
        return abs(self.encoderr.getValue() - self.rref)

    def angle(self):
        x = self.gyro.get_angle()
        return x - self.angleref if x is not None else None

    def fwd(self, v, cm):
        self.reset(kp=500, ki=300, kd=10, speed=v, max_control=30000)
        while self.encl() < config.cm_to_enc(cm) or self.encr() < config.cm_to_enc(cm):
            err = self.angle()
            if err is None:
                continue

            self.iter(err)
        
        self.wheels.stop()

    def turn(self, deg):
        errors = [5 for _ in range(10)]

        self.reset(kp=400, ki=0, kd=0, speed=0, max_control=20000)
        while True:
            angle = self.angle()
            if angle is None:
                continue

            err = angle - deg

            if abs(err) < 15:
                self.params['max_control'] = 12000
                self.params['kp'] = 900

            if abs(err) < 10:
                self.params['max_control'] = 14000
                self.params['kp'] = 5000

            self.iter(err)

            for i in range(10-1):
                errors[i] = errors[i+1]

            errors[10-1] = abs(err)

            if sum(errors) < 15:
                break

        self.wheels.stop()
