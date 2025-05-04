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

i2c = board.I2C()
GPIO.setmode(GPIO.BCM)

camera = Camera()
eyes = Eyes(i2c)
gyro = Gyro()
wheels = Wheels()
encoderl = Encoder(config.ENCODERL_PIN1, config.ENCODERL_PIN2)
encoderr = Encoder(config.ENCODERR_PIN1, config.ENCODERR_PIN2)
driver = Driver(wheels, encoderl, encoderr, gyro)
turbine = Turbine()
line = Line()

graph = {}
nextpos = 0

class GoHome(Exception):
    def __init__(self, pos, dir):
        super().__init__("")

        self.pos = pos
        self.dir = dir

def can_go(x):
    return x > 700

def cannot_go(x):
    return x < 80

def turn_left():
    driver.turn(-90)

def turn_right():
    driver.turn(90)

def reverse():
    driver.turn(180)

def kill_candle():
    print('ROOM', flush=True)

    to_center()
    wheels.stop()
    time.sleep(0.5)

    found = False

    driver.turn(90)    
    time.sleep(0.5)
    
    wheels.go(10000, -10000)

    driver.reset()
    while driver.encl() < config.deg_to_enc(180) or driver.encr() < config.deg_to_enc(180):
        data = camera.read()
        if data is not None:
            found = True
            print('FOUND', flush=True)
            break

    if not found:
        print('NO CANDLE', flush=True)
        return False

    wheels.stop()
    turn_enc = (driver.encl() + driver.encr()) // 2

    time.sleep(0.5)

    driver.reset(config.DRIVER_CANDLE_PARAMS)
    while True:
         data = camera.read()
         if data is None:
            print('LOST CANDLE', flush=True)
            wheels.go(0, 0)
            continue

         (err, area) = data

         print(area, err, flush=True)

         if area > 100:
            break

         driver.iter(err)

    wheels.stop()
    fwd_enc = (driver.encl() + driver.encr()) // 2
    
    turbine.on()
    driver.turn(30)
    driver.turn(30)
    driver.turn(30)
    driver.turn(30)
    turbine.off()

    driver.fwd(-10000, 10)
    
    driver.reset()
    wheels.go(10000, -10000)
    while driver.encl() < config.deg_to_enc(180) - turn_enc or driver.encr() < config.deg_to_enc(180) - turn_enc:
        time.sleep(0.001)

    wheels.stop()
    print(5 / 0)

    return True

def drive_edge():
    driver.reset()
    while True:
        [left, center, right, leftdetect, rightdetect] = eyes.see()
        print(f'{left} {center} {right} | {leftdetect} {rightdetect}', flush=True)

        err = left - right
        driver.iter(err)

        if line.check_room():
            return kill_candle()

        if cannot_go(center):
            wheels.stop()
            return False

        if can_go(leftdetect) or can_go(rightdetect):
            return to_center()

def to_center():
    driver.fwd(20000, 20)
    #[left, right] = eyes.see([3, 4])

    #if not can_go(left):
    #    print('ALIGN LEFT', flush=True)

    #    driver.reset()
    #    while driver.encl() < config.cm_to_enc(20) or driver.encr() < config.cm_to_enc(20):
    #        [left] = eyes.see([0])

    #        err = left - 350
    #        driver.iter(err)

    #        if line.check_room():
    #            return kill_candle()
    #elif not can_go(right):
    #    print('ALIGN RIGHT', flush=True)

    #    driver.reset()
    #    while driver.encl() < config.cm_to_enc(20) or driver.encr() < config.cm_to_enc(20):
    #        [right] = eyes.see([2])

    #        err = 350 - right
    #        driver.iter(err)

    #        if line.check_room():
    #            return kill_candle()
    #else:
    #    print('BLIND', flush=True)

    #    driver.fwd(20000, 25000, 20)

def from_center():
    [left, right] = eyes.see([0, 2])

    if not can_go(left) and not can_go(right):
        print('SKIP', flush=True)
        pass
    elif not can_go(left):
        print('ALIGN LEFT', flush=True)

        driver.reset(max_control=10000)
        while can_go(right):
            [left, right] = eyes.see([0, 4])

            err = left - 350
            driver.iter(err)

        driver.reset(max_control=10000)
        while driver.encl() < config.cm_to_enc(15) or driver.encr() < config.cm_to_enc(15):
            [left] = eyes.see([0])

            err = left - 350
            driver.iter(err)
    elif not can_go(right):
        print('ALIGN RIGHT', flush=True)

        driver.reset(max_control=10000)
        while can_go(left):
            [left, right] = eyes.see([3, 2])

            err = 350 - right
            driver.iter(err)

        driver.reset(max_control=10000)
        while driver.encl() < config.cm_to_enc(15) or driver.encr() < config.cm_to_enc(15):
            [right] = eyes.see([2])

            err = 350 - right
            driver.iter(err)
    else:
        print('BLIND', flush=True)
        driver.fwd(20000, 15)

    wheels.stop()
    time.sleep(0.5)

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
    #if pos == 0:
    #    next.append(180)

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

        from_center()

        if drive_edge():
            raise GoHome(pos, newdir)

        dir = find_candle(newpos, newdir)
        print(f'! STUCK {newpos} @ {dir}', flush=True)

        targetdir = revert(newdir)
        reldir = to_rel(dir, targetdir)
        dir = targetdir

        print(f'? EXIT {targetdir}', flush=True)
        print(f'* EXEC {reldir}', flush=True)

        if reldir == -90:
            turn_left()
            from_center()
        elif reldir == 90:
            turn_right()
            from_center()
        elif reldir == 180:
            driver.fwd(-15000, 10)
            reverse()

        drive_edge()

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

print('====================== START ======================', flush=True)


try:
    #while True:
    #    print(eyes.see(), flush=True)
    #driver.fwd(30000, 1000)
    #time.sleep(1000)
    #wheels.stop()
    #driver.turn(180)
    #time.sleep(1)
    #driver.turn(-180)
    #time.sleep(1000)
    #driver.fwd(-15000, 20)
    #drive_edge()
    #driver.reset()
    #while driver.encl() < config.cm_to_enc(40) or driver.encr() < config.cm_to_enc(40):
    #    err = 300 - eyes.see(2)
    #    driver.iter(err)

    #drive_edge()
    #reverse()
    #driver.fwd(15000, 20)
    #driver.turn(10000, 40)
    #driver.turn(15000, 90)
    #driver.fwd(15000, 100)
    #driver.fwd(-15000, 70)
    #turbine.on()
    #time.sleep(2)
    #turbine.off()
    #time.sleep(1000)
    #driver.fwd(-10000, 5)
    #reverse()

    #while True:
    #    drive_edge()
    #    time.sleep(0.5)

    #    turn_right()

    #    # GOOD!
    #    driver.reset(kd=0.4)
    #    while driver.encl() < config.cm_to_enc(35) or driver.encr() < config.cm_to_enc(35):
    #        err = eyes.see(0) - 300
    #        driver.iter(err)

    #    drive_edge()
    #    driver.fwd(-15000, 5)
    #    time.sleep(0.5)

    #    reverse()

    #    drive_edge()
    #    time.sleep(0.5)

    #    turn_left()

    #    driver.reset(kd=0.4)
    #    while driver.encl() < config.cm_to_enc(35) or driver.encr() < config.cm_to_enc(35):
    #        err = 300 - eyes.see(2)
    #        driver.iter(err)

    #    drive_edge()
    #    driver.fwd(-15000, 5)
    #    time.sleep(0.5)

    #    reverse()

    #drive_edge()
    #driver.reset(config.DRIVER_CANDLE_PARAMS)
    #while True:
    #    err = camera.err()
    #    if err is None:
    #        err = 0

    #    driver.iter(err)

    #    dist = camera.dist()
    #    print(dist, flush=True)
    #    if dist is not None and dist > 30:
    #        print(5 / 0)
    #        break
            #wheels.stop()
            #turbine.on()
            #time.sleep(1)
            #turbine.off()

    #wheels.go(20000, 20000)
    #enc = 0
    #while enc < 3000:
    #    enc = (encoderl.getValue() + encoderr.getValue()) // 2
    #    print(enc)

    #wheels.stop()

    #graph = {0: {1: 270}, 1: {0: 90, 2: 180}, 2: {1: 0, 3: 270}, 3: {2: 90, 4: 270}, 4: {3: 90}} 
    #return_home(4, 270)

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
