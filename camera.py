import mlx.mlx90640 as mlx
import cv2 as cv
import numpy as np
import time

class Camera:
    def __init__(self):
        print('INIT camera', flush=True)

        while True:
            try:
                self.cam = mlx.Mlx9064x('I2C-1', frame_rate=32)
                self.cam.init()
                break

            except OSError as e:
                print('FAILURE camera', flush=True)
                print('<><><><><>RETRY in 2s<><><><><><>', flush=True)
                time.sleep(2)

        print('SUCCESS camera', flush=True)

    def deinit(self):
        print('DEINIT camera', flush=True)

    def read(self):
        try:
            frame = self.cam.read_frame()
            frame = self.cam.do_compensation(frame)
            frame = np.array(frame, dtype=np.float32)

            im = np.reshape(frame, (24, 32))
            im = cv.flip(im, 1)

            thresh = im > 28
            thresh = thresh.astype(np.uint8)
            contours, _ = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

            contours = sorted(contours, key=cv.contourArea, reverse=True)
            if len(contours) == 0:
                return None

            contour = contours[0]

            area = cv.contourArea(contour)

            M = cv.moments(contours[0])
            if M['m00'] == 0:
                return None

            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])

            err = 16 - cx
            return (err, area)

        except OSError:
            return None
