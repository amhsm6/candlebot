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
#from line import Line

i2c = board.I2C()
GPIO.setmode(GPIO.BCM)

camera = Camera()
eyes = Eyes(i2c)
wheels = Wheels()
encoderl = Encoder(config.ENCODERL_PIN1, config.ENCODERL_PIN2)
encoderr = Encoder(config.ENCODERR_PIN1, config.ENCODERR_PIN2)
driver = Driver(wheels, encoderl, encoderr)
turbine = Turbine()
#line = Line()

graph = {}
nextpos = 0

class GoHome(Exception):
    def __init__(self, pos, dir):
        super().__init__("")

        self.pos = pos
        self.dir = dir

def can_go(x):
    return x > 700 or x == 0

def cannot_go(x):
    return x < 100

def turn_left():
    driver.turn(-10000, 85)

def turn_right():
    driver.turn(10000, 85)

def reverse():
    driver.turn(10000, 180)

# FIXME
def kill_candle():
    # drive around the room while checking for candle
    # when found, run driver until close
    # extinguish
    # return
    pass

def drive_edge():
    driver.reset()
    while True:
        [left, center, right] = eyes.see()
        print(f'{left} {center} {right}', flush=True)

        err = left - right
        driver.iter(err)

        #if line.check_room():
        #    kill_candle()
        #    return True

        if cannot_go(center):
            wheels.stop()
            return False

        if can_go(left) or can_go(right):
            driver.fwd(config.DRIVER_WALL_PARAMS['speed'], 20)
            return False

def from_center():
    dists = eyes.see()
    print(f'from_center {dists[0]} {dists[1]} {dists[2]}', flush=True)
    if not can_go(dists[0]):
        driver.reset(kd=0.4)
        while driver.encl() < config.cm_to_enc(35) or driver.encr() < config.cm_to_enc(35):
            err = eyes.see(0) - 300
            driver.iter(err)
    elif not can_go(dists[2]):
        driver.reset(kd=0.4)
        while driver.encl() < config.cm_to_enc(35) or driver.encr() < config.cm_to_enc(35):
            err = 300 - eyes.see(2)
            driver.iter(err)
    else:
        driver.fwd(15000, 35)

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
    next = []

    dists = eyes.see()
    print(f'{dists[0]} {dists[1]} {dists[2]}', flush=True)
    for i, d in enumerate(dists):
        if can_go(d):
            reldir = (i - 1) * 90
            next.append(to_abs(dir, reldir))
    
    return next

def find_candle(pos, dir):
    print(f'ENTER {pos} @ {dir}', flush=True)
    print(graph)

    next = next_paths(dir)
    if pos == 0:
        next.append(180)

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
            reverse()

        time.sleep(2)
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
    #driver.turn(-15000, 90)
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
#line.deinit()
