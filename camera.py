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
        im = cv.flip(im, -1)

        return im

    def err(self):
        im = self.read()

        im = cv.resize(im, (320, 240))

        thresh = im > 30.0
        thresh = thresh.astype(np.uint8)
        contours, _ = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        contours = sorted(contours, key=cv.contourArea, reverse=True)
        if len(contours) == 0:
            return None

        contour = contours[0]

        M = cv.moments(contour)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])

        err = 160 - cx
        return err
