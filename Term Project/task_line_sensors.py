from line_sensor import SensorArray
from task_share import Share

class Task_Line_Sensor:
    def __init__(self,cal_white:Share,cal_black:Share,centroid:Share,
                 line_sensors:SensorArray):
        '''`Task_Line_Sensor` task manages the calibration and operation of a 
        `SensorArray` used for line tracking. It calibrates the sensors for 
        both white and black surfaces, then continuously reads sensor values to 
        calculate the black line relative to the array.
        
        :param line_sensors: A `SensorArray` object that detects surface contrast.
        :param cal_white: A share set by `Task_Repl` indicating when to perform 
            white surface calibration.
        :param cal_black: A share set by `Task_Repl` indicating when to perform 
            black surface calibration.

        :return centroid: Shares the position of the detected black line 
            relative to the sensor array.
        '''
        
        # Copy parameters to properties
        self.cal_white = cal_white
        self.cal_black = cal_black
        self.centroid = centroid
        self.line_sensors = line_sensors

        # States of the FSM
        self.S0_WHITE = 0
        self.S1_BLACK = 1
        self.S2_RUN   = 2

        # Preinitialization
        # This code before the loop initializes the Python code and structure of
        # FSM but does not initialize the FSM itself
        self.state = self.S0_WHITE

    def task(self):

        while True:
            if self.state == self.S0_WHITE:
                if self.cal_white.get():
                    self.line_sensors.calibrate_all("white")
                    self.state = self.S1_BLACK

            elif self.state == self.S1_BLACK:
                if self.cal_black.get():
                    self.line_sensors.calibrate_all("black")
                    prev_centroid = 7
                    self.state = self.S2_RUN

            elif self.state == self.S2_RUN:
                self.line_sensors.read_all()
                centroid = self.line_sensors.get_centroid()
                if centroid < 1:
                    centroid = prev_centroid

                self.centroid.put(centroid)

                prev_centroid = centroid

            else:
                raise ValueError("Invalid State")
            
            yield self.state