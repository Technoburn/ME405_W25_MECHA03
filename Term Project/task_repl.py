from task_share import Share
from nb_input import NB_Input
from boot import BT_ser
from gc import collect

class Task_Repl:
    def __init__(self,sys:Share,gyro:Share,acc:Share,mag:Share,run:Share,
                 cal_white:Share,cal_black:Share):
        '''The `Task_Repl` task manages non-blocking Bluetooth communication, 
        ensures IMU and line sensor calibration, and signals other tasks when 
        to start running.
        
        :param sys: A `share` for IMU system calibration status.
        :param gyro: A `share` for  IMU gyroscope calibration status.
        :param acc: A `share` for IMU accelerometer calibration status.
        :param mag: A `share` for IMU magnetometer calibration status.
        :param BT_ser: Bluetooth serial interface for non-blocking input created
         in `boot.py`.

        :return run: A `share` indicating when to start running the motors.
        :return cal_white: A `share` signaling when to calibrate white sensor 
            values.
        :return cal_black: A `share` signaling when to calibrate black sensor 
            values.
        '''

        # Copy parameters to properties
        self.run = run
        self.sys, self.gyro, self.acc, self.mag = (sys, gyro, acc, mag)
        self.cal_white = cal_white
        self.cal_black = cal_black

        # States of the FSM
        self.S0_INIT    = 0
        self.S1_CAL_IMU = 1
        self.S2_WHITE   = 2
        self.S3_BLACK   = 3
        self.S4_RUN     = 4

        # Preinitialization
        # This code before the loop initializes the Python code and structure of FSM
        # but does not initialize the FSM itself
        self.state = self.S0_INIT

    def task(self):

        while True:
            collect() # Run Garbage Collection

            if self.state == self.S0_INIT:
                nb_in = NB_Input(BT_ser)
                
                # Intitialize shared values
                self.run.put(False)
                self.cal_black.put(False)

                if not all((self.sys.get(),self.gyro.get(),
                           self.acc.get(),self.mag.get())):
                    print("\nCalibration needed")
                    self.state = self.S1_CAL_IMU
                else:
                    print("\nIMU Calibrated\nPress Enter To Calibrate white:")
                    self.state = self.S2_WHITE

            elif self.state == self.S1_CAL_IMU:
                print(self.sys.get(),self.gyro.get(),
                      self.acc.get(),self.mag.get())

                if all((self.sys.get(),self.gyro.get(),
                       self.acc.get(),self.mag.get())):
                    print("\nIMU Calibrated\nPress Enter To Calibrate white:")
                    self.state = self.S2_WHITE

            elif self.state == self.S2_WHITE:
                if nb_in.any():
                    nb_in.get() # Clear value in input
                    self.cal_white.put(True)
                    print("\nPress Enter To Calibrate black:")
                    self.state = self.S3_BLACK

            elif self.state == self.S3_BLACK:
                if nb_in.any():
                    nb_in.get() # Clear value in input
                    self.cal_black.put(True)
                    print("\nPress Enter To Run:")
                    self.state = self.S4_RUN

            elif self.state == self.S4_RUN:
                if nb_in.any():
                    nb_in.get() # Clear value in input
                    self.run.put(True)
                    print("\nRunning...")

            else:
                raise ValueError("Invalid State")
            
            yield self.state