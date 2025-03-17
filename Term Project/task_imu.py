from imu import BNO055
from time import ticks_ms,ticks_diff
from task_share import Share

class Task_IMU:
    def __init__(self,sys:Share,gyro:Share,acc:Share,mag:Share,heading:Share,
                 yaw_rate:Share,imu:BNO055):
        '''Initializes and continuously reads data from a BNO055 Inertial 
        Measurement Unit (IMU). It ensures the IMU is calibrated and shares yaw
        rate and heading data with other tasks in the system.

        :param imu: An IMU sensor that provides orientation and angular 
            velocity data.
        :param sys,gyro,acc,mag: Shared objects that store calibration status 
            for different IMU subsystems.
        
        :return heading: Shares the IMU's calculated `heading angle`.
        :return yaw_rate: Shares the `yaw_rate`, the angular velocity around the 
        vertical axis.        
        '''
        
        
        # Copy parameters to properties
        self.heading = heading
        self.yaw_rate = yaw_rate
        self.sys, self.gyro, self.acc, self.mag = (sys, gyro, acc, mag)
        self.imu = imu

        # States of the FSM
        self.S0_INIT    = 0
        self.S1_CAL_IMU = 1
        self.S2_RUN     = 2

        # Preinitialization
        # This code before the loop initializes the Python code and structure of
        # FSM but does not initialize the FSM itself
        self.state = self.S0_INIT

    def task(self):
        '''Generator Function to run implemented Finite-State Machine'''

        while True:
            if self.state == self.S0_INIT:
                try:
                    # Write Calibration data to IMU
                    self.imu.write_calibration()

                    self.sys.put(True)
                    self.gyro.put(True)
                    self.acc.put(True)
                    self.mag.put(True)

                    self.state = self.S2_RUN

                except OSError:
                    # Get calibration status
                    sys, gyro, acc, mag = self.imu.get_status()

                    # Put all status booleans in shares
                    self.sys.put(sys)
                    self.gyro.put(gyro)
                    self.acc.put(acc)
                    self.mag.put(mag)

                    self.state = self.S1_CAL_IMU

            elif self.state == self.S1_CAL_IMU:
                    # Get calibration status
                    sys, gyro, acc, mag = self.imu.get_status()

                    # Put all status booleans in shares
                    self.sys.put(sys)
                    self.gyro.put(gyro)
                    self.acc.put(acc)
                    self.mag.put(mag)

                    if all((sys,gyro,acc,mag)):
                        self.imu.read_calibration()
                        self.state = self.S2_RUN

            elif self.state == self.S2_RUN:
                raw_heading, = self.imu.get_value(BNO055.reg.EUL_HEADING)
                yaw_rate, = self.imu.get_value(BNO055.reg.GYRO_YAW_RATE)

                self.yaw_rate.put(yaw_rate/900)
                self.heading.put(self.imu.angle_diff(0,raw_heading/16))

            else:
                raise ValueError("Invalid State")
            
            yield self.state