import board
from enum import Enum
import time

from camera import Camera
from driver import Driver
from eyes import Eyes
from turbine import Turbine
from wheels import Wheels

i2c = board.I2C()
#camera = Camera()
eyes = Eyes(i2c)
wheels = Wheels()
driver = Driver(wheels, eyes)
turbine = Turbine()

class Edge(Enum):
    STRAIGHT = 0
    LEFT = 1
    RIGHT = 2

    def invert(self):
        if self == Edge.STRAIGHT:
            return Edge.STRAIGHT
        elif self == Edge.LEFT:
            return Edge.RIGHT
        elif self == Edge.RIGHT:
            return Edge.LEFT
        else:
            raise Exception("Impossible Edge variant: {}")

graph = {}

def drive_edge():
    driver.reset()
    while True:
        driver.iter()

        # FIXME: move forward
        if eyes.see(0) > 500 and eyes.see(1) > 500:
            return 0

        if eyes.see(1) > 500:
            return 1

        if eyes.see(0) > 500:
            return -1

# FIXME
def turn_left():
    pass

def turn_right():
    pass

def find_candle():
    graph[0] = { 1: Edge.STRAIGHT }
    graph[1] = { 0: Edge.STRAIGHT }
    pos = 1

    free = drive_edge()
    while True:
        print(f'ENTER {pos}')

        # TODO: check for candle
        print(f'-> NO CANDLE')

        print(f'CAN GO:')

        edge = None
        if free == 1 or free == 0:
            print(f'| Right')
            turn_right()
            edge = Edge.RIGHT
        elif free == -1:
            print(f'| Left')
            turn_left()
            edge = Edge.LEFT
        else:
            print(f'| Straight')
            edge = Edge.STRAIGHT # FIXME
            raise Exception(f'Unexpected value for free: {free}')

        print(f'=== CHOOSE {edge}')
        print(f'*** EXEC')

        free = drive_edge()
        
        newpos = pos + 1

        if pos in graph:
            graph[pos][newpos] = edge
        else:
            graph[pos] = { newpos: edge }

        if newpos in graph:
            graph[newpos][pos] = edge.invert()
        else:
            graph[newpos] = { pos: edge.invert() }

        print(f'??? GRAPH: {graph}')

        pos = newpos

try:
    driver.reset()
    while True:
        driver.iter()

        #im = camera.read()
        #for row in range(24):
        #    for col in range(32):
        #        print(f'{im[row, col]:.2f}', end=' ')

        #    print()

        #print('=' * 15)

except KeyboardInterrupt:
    print()

#camera.deinit()
eyes.deinit()
wheels.deinit()
driver.deinit()
turbine.deinit()
