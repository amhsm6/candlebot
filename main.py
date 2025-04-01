import heapq
#import board
import time
import config
import RPi.GPIO as GPIO

#from camera import Camera
#from driver import Driver
#from eyes import Eyes
from turbine import Turbine
from wheels import Wheels
from encoder import Encoder
#from line import Line

#i2c = board.I2C()
GPIO.setmode(GPIO.BCM)

#camera = Camera()
#eyes = Eyes(i2c)
wheels = Wheels()
#driver = Driver(wheels, eyes)
turbine = Turbine()
encoderl = Encoder(config.ENCODERL_PIN1, config.ENCODERL_PIN2)
encoderr = Encoder(config.ENCODERR_PIN1, config.ENCODERR_PIN2)
#line = Line()

graph = {}
nextpos = 0

class GoHome(Exception):
    def __init__(self, pos, dir):
        super().__init__("")

        self.pos = pos
        self.dir = dir

def can_go(i):
    return bool(int(input(f'CAN GO {i}? ')))
#    return eyes.see(i) > 300

# FIXME
def turn_left():
    print('TURN_LEFT')
    pass

def turn_right():
    print('TURN_RIGHT')
    pass

def reverse():
    print('REVERSE')
    pass

def kill_candle():
    pass

def drive_edge():
    print('DRIVE_EDGE')
    if int(input('KILL CANDLE????? ')) == 1:
        return True
    return False
    #driver.reset()
    #while True:
    #    driver.iter()

    #    if line.check_room():
    #        kill_candle()
    #        return True

    #    if not can_go(1) or can_go(0) or can_go(2):
    #        driver.stop()
    #        time.sleep(2)
    #        return False

def revert(dir):
    return (180 + dir) % 360

def rel(dir, newdir):
    reldir = (newdir - dir) % 360
    if reldir == 270:
        reldir = -90
    return reldir

def abs(dir, reldir):
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

    for i in range(3):
        if not can_go(i):
            continue

        reldir = (i - 1) * 90
        next.append(abs(dir, reldir))
    
    return next

def find_candle(pos, dir):
    print(f'ENTER {pos} @ {dir}')
    print(graph)

    next = next_paths(dir)
    print(f'NEXT: {next}')

    for newdir in next:
        newpos = update_graph(pos, newdir)
        print(f'>=> {pos} @ {dir} -> {newpos} @ {newdir}')

        reldir = rel(dir, newdir)
        print(f'* EXEC {reldir}')
        if reldir == -90:
            turn_left()
        elif reldir == 90:
            turn_right()

        #wheels.go(50000, 50000)
        #time.sleep(2)
        #wheels.stop()
        #time.sleep(2)

        if drive_edge():
            raise GoHome(pos, newdir)

        dir = find_candle(newpos, newdir)
        print(f'! STUCK {newpos} @ {dir}')

        targetdir = revert(newdir)
        reldir = rel(dir, targetdir)
        dir = targetdir

        print(f'? EXIT {targetdir}')
        print(f'* EXEC {reldir}')

        if reldir == -90:
            turn_left()
        elif reldir == 90:
            turn_right()
        elif reldir == 180:
            reverse()

        drive_edge()

    return dir

def return_home(pos, dir):
    print(graph)
    target = 0

    queue = [(0, pos)]
    dist = {pos: 0}
    par = {pos: None}

    visited = set()
    while len(queue):
        (d, x) = heapq.heappop(queue)

        if x == target:
            break

        print(f'VISIT {x} DIST {d}')

        visited.add(x)

        for y in graph[x]:
            print(f' NEXT {y}')

            d = d + 1
            if y not in dist or d < dist[y]:
                print(f' UPD {y} -> {d}: {graph[x][y]}')
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
    print(path)

print('====================== START ======================')

try:
    wheels.go(20000, 20000)
    enc = 0
    while enc < 3000:
        enc = (encoderl.getValue() + encoderr.getValue()) // 2
        print(enc)

    wheels.stop()

    #graph = {0: {1: 270}, 1: {0: 90, 2: 180}, 2: {1: 0, 3: 270}, 3: {2: 90, 4: 270}, 4: {3: 90}} 
    #return_home(4, 270)

    #try:
    #    find_candle(0, 0)
    #except GoHome as e:
    #    return_home(e.pos, e.dir)

#    turbine.set(4000)
#    time.sleep(10)
    #wheels.go(1000, 60000)
    #while True:
    #    print(encoder.getValue())
    #    time.sleep(1)
#        lsb = GPIO.input(Encoder.FWD)
#        msb = GPIO.input(Encoder.REV)
#
#        encoded = (msb << 1) | lsb
#        sum = (self.last_encoded << 2) | encoded;
#
#        if sum == 0b1101 or sum == 0b0100 or sum == 0b0010 or sum == 0b1011:
#            self.value -= 1
#
#        if sum == 0b1110 or sum == 0b0111 or sum == 0b0001 or sum == 0b1000:
#            self.value += 1
#
#        self.last_encoded = encoded
#        pass
#        print(encoder.value)
    #time.sleep(3)
    #turbine.set(4500)
    #time.sleep(10)
    
#    driver.reset()
#    while True:
#        driver.iter()

        #im = camera.read()
        #for row in range(24):
        #    for col in range(32):
        #        print(f'{im[row, col]:.2f}', end=' ')

        #    print()

        #print('=' * 15)

except KeyboardInterrupt:
    print()

print('====================== END ======================')

#camera.deinit()
#eyes.deinit()
wheels.deinit()
#driver.deinit()
turbine.deinit()
encoder.deinit()
