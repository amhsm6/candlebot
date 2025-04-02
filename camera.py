import mlx.mlx90640 as mlx
import cv2 as cv
import numpy as np

class Camera:
    def __init__(self):
        print('INIT camera')

        self.cam = mlx.Mlx9064x('I2C-1', frame_rate=32)
        self.cam.init()

    def deinit(self):
        print('DEINIT camera')

    def read(self):
        try:
            frame = self.cam.read_frame()
            frame = self.cam.do_compensation(frame)
            frame = np.array(frame, dtype=np.float32)

            im = np.reshape(frame, (24, 32))
            im = cv.flip(im, -1)

            return im
        except OSError:
            return None

    def err(self):
        im = self.read()
        if im is None:
            return None

        im = cv.resize(im, (320, 240))

        thresh = im > 30.0
        thresh = thresh.astype(np.uint8)
        contours, _ = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        contours = sorted(contours, key=cv.contourArea, reverse=True)
        if len(contours) == 0:
            return None

        contour = contours[0]

        M = cv.moments(contour)
        if M['m00'] == 0:
            return None

        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])

        err = 160 - cx
        return err
