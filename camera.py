import mlx.mlx90640 as mlx
import cv2 as cv
import numpy as np

class Camera:
    def __init__(self):
        print('INIT camera')

        self.cam = mlx.Mlx9064x('I2C-1', frame_rate=16)
        self.cam.init()

    def deinit(self):
        print('DEINIT camera')

    def read(self):
        frame = self.cam.read_frame()
        frame = self.cam.do_compensation(frame)
        frame = np.array(frame, dtype=np.float32)

        im = np.reshape(frame, (24, 32))
        im = cv.flip(im, 1)

        return im
