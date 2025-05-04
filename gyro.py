import mpu6050
import math
import time

class Gyro:
    def __init__(self):
        print('INIT gyro', flush=True)

        self.mpu6050 = mpu6050.mpu6050(0x68)
        self.gyro_angle_x = 0
        self.gyro_angle_y = 0
        self.gyro_angle_z = 0
        self.calibrate()
        self.reset()

    def deinit(self):
        print('DEINIT gyro', flush=True)

    def reset(self):
        self.t = time.time()

    def calibrate(self):
        accErrorX = 0
        accErrorY = 0
        for _ in range(200):
            accelerometer_data = self.mpu6050.get_accel_data()

            AccX = accelerometer_data['x']
            AccY = accelerometer_data['y']
            AccZ = accelerometer_data['z']

            try:
                accErrorX += (math.atan(AccY / math.sqrt(AccX * AccX + AccZ * AccZ)) * 180 / math.pi)
                accErrorY += (math.atan(-1 * AccX / math.sqrt(AccY * AccY + AccZ * AccZ)) * 180 / math.pi)
            except:
                pass

        self.acc_error_x = accErrorX / 200
        self.acc_error_y = accErrorY / 200

        gyroErrorX = 0
        gyroErrorY = 0
        gyroErrorZ = 0
        for _ in range(200):
            gyroscope_data = self.mpu6050.get_gyro_data()

            gyro_x = gyroscope_data['x']
            gyro_y = gyroscope_data['y']
            gyro_z = gyroscope_data['z']

            gyroErrorX += gyro_x
            gyroErrorY += gyro_y
            gyroErrorZ += gyro_z

        self.gyro_error_x = gyroErrorX / 200
        self.gyro_error_y = gyroErrorY / 200
        self.gyro_error_z = gyroErrorZ / 200

    def get_angles(self):
        accelerometer_data = self.mpu6050.get_accel_data()
        gyroscope_data = self.mpu6050.get_gyro_data()

        AccX = accelerometer_data['x']
        AccY = accelerometer_data['y']
        AccZ = accelerometer_data['z']

        gyro_x = gyroscope_data['x'] - self.gyro_error_x
        gyro_y = gyroscope_data['y'] - self.gyro_error_y
        gyro_z = gyroscope_data['z'] - self.gyro_error_z

        try:
            accAngleX = (math.atan(AccY / math.sqrt(AccX * AccX + AccZ * AccZ)) * 180 / math.pi) - self.acc_error_x
            accAngleY = (math.atan(-1 * AccX / math.sqrt(AccY * AccY + AccZ * AccZ)) * 180 / math.pi) - self.acc_error_y
        except:
            accAngleX = 0
            accAngleY = 0

        t_prev = self.t
        self.t = time.time()
        elapsed = self.t - t_prev

        self.gyro_angle_x += gyro_x * elapsed
        self.gyro_angle_y += gyro_y * elapsed
        self.gyro_angle_z += gyro_z * elapsed

        return [
             0.96 * self.gyro_angle_x + 0.04 * accAngleX,
             0.96 * self.gyro_angle_y + 0.04 * accAngleY,
             -self.gyro_angle_z
        ]

    def get_angle(self):
        try:
            return self.get_angles()[2]
        except:
            return None
