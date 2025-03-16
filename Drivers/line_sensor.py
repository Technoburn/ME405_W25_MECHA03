from pyb import Pin,ADC,udelay,delay

class LineSensor:
    '''Single channel IR line sensor interface encapsulated in a Python class'''

    def __init__(self, adc_Pin:Pin, num:int):
        '''Initializes a Line Sensor Object

        :param adc_Pin: Analog input pin for line sensor
        :param num: number associated with sensor
        '''

        self.adc = ADC(adc_Pin)
        '''Sensor ADC Object'''
        self.num = num
        '''Number associated with sensor channel'''
        self.white_val = 250
        '''Calibrated value for white'''
        self.black_val = 4000
        '''Calibrated value for black'''

    def calibrate_white(self):
        '''Calibrate the sensor to what value represents white'''
        self.white_val = self.adc.read()

    def calibrate_black(self):
        '''Calibrate the sensor to what value represents black'''
        self.black_val = self.adc.read()

    def read(self) -> float:
        '''Read the light sensor and return a normalized value
        taking into account calibration
        
        :return: Normalized light level between 0 and 1
        :rtype: float    
        '''
        sensor_value = self.adc.read()

        # Normalize sensor value
        normal = (sensor_value-self.white_val)/(self.black_val-self.white_val)

        # Return limited normalized value
        return max(min(normal,1),0)

class SensorArray:
    '''Multi-channel IR Line Sensor interface'''

    def __init__(self, CNTRL:Pin, sensor_define:list[tuple[Pin,int]]):
        '''Initializes a Line Sensor Array object

        :param CNTRL: Sensor dimming control pin for line sensor array
        :param sensor_define: List of tuples, (ADC Pin, number associated 
            for each sensor)
        '''

        self.CNTRL = Pin(CNTRL, mode = Pin.OUT_PP)
        '''Sensor dimming control pin'''
        self.sensor_list = [LineSensor]*len(sensor_define)
        '''List of line sensors in the array'''
        self.dimm_lvl = 0
        '''Current Dimming level of the array'''
        self.sensor_values = [float]*len(sensor_define)
        '''Most recent read sensor values'''
        
        for idx,sensor in enumerate(sensor_define):
            self.sensor_list[idx] = LineSensor(sensor[0],sensor[1])
            self.sensor_values[idx] = self.sensor_list[idx].read()

    def dimm(self):
        '''Reduce the emitting level of the light sensors array by 3.33%
        '''

        # Send 1 us pulse to dim by 1 level
        self.CNTRL.low()
        udelay(10)
        self.CNTRL.high()

        # Update current dimming level
        if self.dimm_lvl == 31:
            self.dimm_lvl = 0
        else:
            self.dimm_lvl += 1

    def calibrate_all(self, color:str):
        '''Calibrate sensors array for a specified color: ("white" or "black")
        
        :param color: String of either "black" or "white", corresponding to 
            what color is being calibrated for
        '''

        # Turn on emmiters"
        self.CNTRL.high()

        udelay(50)

        #white Calibration
        if color == "white":
            for sensor in self.sensor_list:
                sensor.calibrate_white()
        
        #black Calibration
        elif color == "black":
            for sensor in self.sensor_list:
                sensor.calibrate_black()
        
        else:
            raise ValueError("Black or White calibration must be selected")
        
        # Turn off emmiters
        self.CNTRL.low()

    def read_all(self) -> list[float]:
        '''Read the light sensor array and return normalized values,
        taking into account calibration
        
        :return: List of floats of normalized light levels between 0 and 1 for
            each light sensor in the array
        :rtype: list[float]    
        '''

        # Turn on emmiters"
        self.CNTRL.high()

        udelay(50)

        for idx,sensor in enumerate(self.sensor_list):
            self.sensor_values[idx] = sensor.read()

        # Turn off emmiters
        self.CNTRL.low()

        return self.sensor_values
    
    def get_centroid(self) -> float:
        '''Calculate the centroid of the distribution light array distribution
        
        :return: centroid of the sensor readings
        :rtype: float
        '''

        first_moment = 0
        area = 1e-10

        # Compute centroid of the sensor readings
        for idx,sensor_reading in enumerate(self.sensor_values):
            first_moment += sensor_reading * self.sensor_list[idx].num
            area += sensor_reading

        return first_moment/area

if __name__ == "__main__":

    sensors_defined = [(Pin.cpu.A1,1),
                       (Pin.cpu.C2,2),
                       (Pin.cpu.A0,3),
                       (Pin.cpu.C3,4),
                       (Pin.cpu.A6,5),
                       (Pin.cpu.C0,6),
                       (Pin.cpu.A7,7),
                       (Pin.cpu.C1,8),
                       (Pin.cpu.C5,9),
                       (Pin.cpu.B0,10),
                       (Pin.cpu.C4,11),
                       (Pin.cpu.A4,12),
                       (Pin.cpu.B1,13)]                  
    
    line_sensors = SensorArray(Pin.cpu.H0, sensors_defined)

    # Calibrates the sensors for black
    input("Press Enter To Calibrate black:")
    line_sensors.calibrate_all("black")

    print([sensor.black_val for sensor in line_sensors.sensor_list])

    # Now calibrtate white values
    input("Press Enter To Calibrate white:")
    line_sensors.calibrate_all("white")
    print([sensor.white_val for sensor in line_sensors.sensor_list])

    # Print out raw sensor readings and centroid
    while True:
        delay(100)
        raw_readings = line_sensors.read_all()
        centroid = line_sensors.get_centroid()
        print(raw_readings,centroid)