import heapq
import board
import time
import config
import RPi.GPIO as GPIO

from camera import Camera
from driver import Driver
from eyes import Eyes
from turbine import Turbine
from wheels import Wheels
from encoder import Encoder
from line import Line
from gyro import Gyro
from button import Button

i2c = board.I2C()
GPIO.setmode(GPIO.BCM)

camera = Camera()
eyes = Eyes(i2c)
gyro = Gyro()
wheels = Wheels()
encoderl = Encoder(config.ENCODERL_PIN1, config.ENCODERL_PIN2)
encoderr = Encoder(config.ENCODERR_PIN1, config.ENCODERR_PIN2)
driver = Driver(wheels, encoderl, encoderr, gyro)
line = Line()
button = Button()
turbine = Turbine()

graph = {}
nextpos = 0

class GoHome(Exception):
    def __init__(self, pos, dir):
        super().__init__("")

        self.pos = pos
        self.dir = dir

def can_go(x):
    return x > 600

def cannot_go(x):
    return x < 150

def turn_left():
    driver.turn(-90)

def turn_right():
    driver.turn(90)

def reverse():
    driver.turn(180)

def kill_candle(dir):
    print('ROOM', flush=True)

    wheels.stop()
    time.sleep(0.1)

    [left, right] = eyes.see([3, 4])

    if not can_go(left) and not can_go(right):
        print('ALIGN BOTH room', flush=True)

        driver.reset(config.DRIVER_WALL_ONESIDE)
        while driver.encl() < config.cm_to_enc(30) or driver.encr() < config.cm_to_enc(30):
            [left, right] = eyes.see([3, 4])

            err = left - right
            driver.iter(err)
    elif not can_go(left):
        print('ALIGN LEFT room', flush=True)

        driver.reset(config.DRIVER_WALL_ONESIDE)
        while driver.encl() < config.cm_to_enc(30) or driver.encr() < config.cm_to_enc(30):
            [left] = eyes.see([3])

            err = left - 300
            driver.iter(err)
    elif not can_go(right):
        print('ALIGN RIGHT room', flush=True)

        driver.reset(config.DRIVER_WALL_ONESIDE)
        while driver.encl() < config.cm_to_enc(30) or driver.encr() < config.cm_to_enc(30):
            [right] = eyes.see([4])

            err = 300 - right
            driver.iter(err)
    else:
        print('ALIGN BLIND room', flush=True)
        driver.fwd(20000, 20)

    driver.turn(-110)
    time.sleep(0.5)
    
    wheels.go(13000, -13000)

    found = False

    driver.reset()
    angle = driver.angle()
    while True:
        data = camera.read()
        if data is not None:
            found = True
            print('FOUND', flush=True)
            break

        angle = driver.angle()
        print(angle, flush=True)

        if angle is not None and angle >= 220:
            break

    wheels.stop()

    if not found:
        print('NO CANDLE', flush=True)
        driver.turn(290 - angle)
        driver.fwd(20000, 10)
        return ((dir + 180) % 360, False)

    time.sleep(0.5)

    prev_enc = 0
    fwd_enc = 0
    driver.reset(config.DRIVER_CANDLE_PARAMS, reset_angle=False)
    while True:
        angle = driver.angle()

        if angle > 600:
            print('NO CANDLE', flush=True)
            driver.turn((290 - angle) % 360)
            return ((dir + 180) % 360, False)

        data = camera.read()
        if data is None:
           print('LOST CANDLE', flush=True)

           wheels.go(12000, -12000)
           continue

        enc = (driver.encl() + driver.encr()) // 2 
        fwd_enc += enc - prev_enc
        print(enc, prev_enc, enc - prev_enc, flush=True)

        (err, area) = data

        print(area, err, flush=True)

        if area > 175:
           break

        driver.iter(err)

        prev_enc = enc

    wheels.stop()
    
    turbine.on()
    time.sleep(3)
    turbine.off()

    print(config.enc_to_cm(fwd_enc) - 10, angle, flush=True)

    driver.fwd(-20000, config.enc_to_cm(fwd_enc) - 10)
    driver.turn(290 - angle)

    to_center(None)
    to_center(None)

    return ((dir + 180) % 360, True)

def drive_edge(dir):
    driver.reset(no_wait=True)
    while True:
        x = eyes.see(detect=dir is not None, line=line)
        if x == "A":
            return kill_candle(dir)

        [left, center, right, leftdetect, rightdetect] = x

        print(f'{left} {center} {right} | {leftdetect} {rightdetect}', flush=True)

        if dir is not None and line.check_room():
            return kill_candle(dir)

        if cannot_go(center):
            wheels.stop()
            return None

        if can_go(leftdetect) or can_go(rightdetect):
            wheels.go(18000, 18000)
            time.sleep(0.1)
            return to_center(dir)

        err = left - right
        driver.iter(err)

def to_center(dir):
    [left, right] = eyes.see([3, 4])

    if not can_go(left):
        print('ALIGN LEFT to_center', flush=True)

        driver.reset(config.DRIVER_WALL_ONESIDE)
        while driver.encl() < config.cm_to_enc(25) or driver.encr() < config.cm_to_enc(25):
            [left] = eyes.see([3])

            err = left - 330
            driver.iter(err)
    
            if dir is not None and line.check_room():
                return kill_candle(dir)
    elif not can_go(right):
        print('ALIGN RIGHT to_center', flush=True)

        driver.reset(config.DRIVER_WALL_ONESIDE)
        while driver.encl() < config.cm_to_enc(25) or driver.encr() < config.cm_to_enc(25):
            [right] = eyes.see([4])

            err = 330 - right
            driver.iter(err)

            if dir is not None and line.check_room():
                return kill_candle(dir)
    else:
        print('BLIND to_center', flush=True)

        driver.reset(kp=500, ki=300, kd=10, speed=20000, max_control=30000)
        while driver.encl() < config.cm_to_enc(25) or driver.encr() < config.cm_to_enc(25):
            err = driver.angle()
            if err is None:
                continue

            driver.iter(err)

            if dir is not None and line.check_room():
                return kill_candle(dir)

    wheels.stop()
    time.sleep(0.5)

    return None

def from_center(dir):
    [left, right] = eyes.see([0, 2])

    if not can_go(left) and not can_go(right):
        print('SKIP from_center', flush=True)
    elif not can_go(left):
        print('ALIGN LEFT from_center', flush=True)

        right = 9999

        driver.reset(config.DRIVER_WALL_ONESIDE)
        while can_go(right):
            [left, right] = eyes.see([0, 4])

            err = left - 330
            driver.iter(err)

            if dir is not None and line.check_room():
                return kill_candle(dir)

        driver.reset(config.DRIVER_WALL_ONESIDE)
        while driver.encl() < config.cm_to_enc(10) or driver.encr() < config.cm_to_enc(10):
            [left] = eyes.see([0])

            err = left - 330
            driver.iter(err)

            if dir is not None and line.check_room():
                return kill_candle(dir)
    elif not can_go(right):
        print('ALIGN RIGHT from_center', flush=True)

        left = 9999

        driver.reset(config.DRIVER_WALL_ONESIDE)
        while can_go(left):
            [left, right] = eyes.see([3, 2])

            err = 330 - right
            driver.iter(err)

            if dir is not None and line.check_room():
                return kill_candle(dir)

        driver.reset(config.DRIVER_WALL_ONESIDE)
        while driver.encl() < config.cm_to_enc(10) or driver.encr() < config.cm_to_enc(10):
            [right] = eyes.see([2])

            err = 330 - right
            driver.iter(err)

            if dir is not None and line.check_room():
                return kill_candle(dir)
    else:
        print('BLIND from_center', flush=True)

        driver.reset(kp=500, ki=300, kd=10, speed=20000, max_control=30000)
        while driver.encl() < config.cm_to_enc(25) or driver.encr() < config.cm_to_enc(25):
            err = driver.angle()
            if err is None:
                continue

            driver.iter(err)

            if dir is not None and line.check_room():
                return kill_candle(dir)

    wheels.stop()
    time.sleep(0.5)

    return None

def revert(dir):
    return (180 + dir) % 360

def to_rel(dir, newdir):
    reldir = (newdir - dir) % 360
    if reldir == 270:
        reldir = -90
    return reldir

def to_abs(dir, reldir):
    return (dir + reldir) % 360

def update_graph(pos, dir):
    global nextpos
    nextpos += 1

    newpos = nextpos

    if pos not in graph:
        graph[pos] = { newpos: dir }
    else:
        graph[pos][newpos] = dir

    revdir = revert(dir)
    if newpos not in graph:
        graph[newpos] = { pos: revdir }
    else:
        graph[newpos][pos] = revdir

    return newpos

def next_paths(dir):
    N = 7

    next = []

    left = []
    center = []
    right = []
    for _ in range(N):
        [l, c, r] = eyes.see([3, 1, 4])

        left.append(l)
        center.append(c)
        right.append(r)

    left.sort()
    center.sort()
    right.sort()

    dists = [left[N // 2], center[N // 2], right[N // 2]]
    print(f'{dists[0]} {dists[1]} {dists[2]}', flush=True)

    for i, d in enumerate(dists):
        if can_go(d):
            reldir = (i - 1) * 90
            next.append(to_abs(dir, reldir))
    
    return next

def find_candle(pos, dir):
    print(f'ENTER {pos} @ {dir}', flush=True)
    print(graph)

    wheels.stop()
    time.sleep(0.2)
    next = next_paths(dir)

    print(f'NEXT: {next}', flush=True)

    for newdir in next:
        newpos = update_graph(pos, newdir)
        print(f'>=> {pos} @ {dir} -> {newpos} @ {newdir}', flush=True)

        reldir = to_rel(dir, newdir)
        print(f'* EXEC {reldir}', flush=True)
        if reldir == -90:
            turn_left()
        elif reldir == 90:
            turn_right()
        elif reldir == 180:
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', flush=True)
            reverse()

        room = None

        x = from_center(newdir)
        if x is not None:
            (room_dir, killed_candle) = x

            if killed_candle:
                raise GoHome(pos, room_dir)

            room = room_dir

        if room is None:
            x = drive_edge(newdir)
            if x is not None:
                (room_dir, killed_candle) = x

                if killed_candle:
                    raise GoHome(pos, room_dir)

                room = room_dir

        dir = find_candle(newpos, newdir) if room is None else room
        print(f'! STUCK {newpos} @ {dir}', flush=True)

        targetdir = revert(newdir)
        reldir = to_rel(dir, targetdir)
        dir = targetdir

        print(f'? EXIT {targetdir}', flush=True)
        print(f'* EXEC {reldir}', flush=True)

        if reldir == -90:
            turn_left()
            from_center(None)
        elif reldir == 90:
            turn_right()
            from_center(None)
        elif reldir == 180:
            driver.fwd(-15000, 5)
            reverse()

        drive_edge(None)

    return dir

def return_home(pos, dir):
    print(graph, flush=True)
    target = 0

    queue = [(0, pos)]
    dist = {pos: 0}
    par = {pos: None}

    visited = set()
    while len(queue):
        (d, x) = heapq.heappop(queue)

        if x == target:
            break

        print(f'VISIT {x} DIST {d}', flush=True)

        visited.add(x)

        for y in graph[x]:
            print(f' NEXT {y}')

            d = d + 1
            if y not in dist or d < dist[y]:
                print(f' UPD {y} -> {d}: {graph[x][y]}', flush=True)
                dist[y] = d
                par[y] = x

            if y not in visited:
                heapq.heappush(queue, (d, y))

    path = []

    curr = target
    while curr is not None:
        path.append(curr)
        curr = par[curr]

    path.reverse()
    print(path, flush=True)

    v = pos
    for u in path[1:]:
        newdir = graph[v][u]

        reldir = to_rel(dir, newdir)
        print(f'* EXEC {reldir}', flush=True)
        if reldir == -90:
            turn_left()
        elif reldir == 90:
            turn_right()
        elif reldir == 180:
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', flush=True)
            reverse()

        from_center(None)
        drive_edge(None)

        v = u

print('====================== START ======================', flush=True)


try:
    #while not button.pressed():
    #    time.sleep(0.001)

    try:
        find_candle(0, 0)
    except GoHome as e:
        return_home(e.pos, e.dir)

except KeyboardInterrupt:
    print(flush=True)

print('====================== END ======================', flush=True)

camera.deinit()
eyes.deinit()
wheels.deinit()
driver.deinit()
turbine.deinit()
encoderl.deinit()
encoderr.deinit()
line.deinit()
gyro.deinit()
