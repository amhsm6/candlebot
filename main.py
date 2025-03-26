import board
import time
import config
import RPi.GPIO as GPIO

#from camera import Camera
#from driver import Driver
#from eyes import Eyes
from turbine import Turbine
from wheels import Wheels
from encoder import Encoder

i2c = board.I2C()
GPIO.setmode(GPIO.BCM)

#camera = Camera()
#eyes = Eyes(i2c)
wheels = Wheels()
#driver = Driver(wheels, eyes)
turbine = Turbine()
encoder = Encoder(config.ENCODER_PIN1, config.ENCODER_PIN2)

graph = {}
nextpos = 0

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

def drive_edge():
    print('DRIVE_EDGE')
    #driver.reset()
    #while True:
        #driver.iter()

        # if detect_room():
        #    return kill_candle()

        #if not can_go(1) or can_go(0) or can_go(2):
        #    driver.stop()
        #    time.sleep(2)
        #    break

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

        drive_edge()

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

print('====================== START ======================')

try:
#    turbine.set(4000)
#    time.sleep(10)
    wheels.go(1000, 60000)
    while True:
        print(encoder.getValue())
        time.sleep(1)
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
#    find_candle(0, 0)
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
