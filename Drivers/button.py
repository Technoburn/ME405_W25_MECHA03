from pyb import Pin,delay

class ButtonSensor:
    '''Single channel Bump Sensor class'''

    def __init__(self, digital_Pin:Pin):
        ''' Initializes a single Bump Sensor Object

        :param digital_Pin: Digital input pin for a single bump sensor
        '''
        self.digital_pin = Pin(digital_Pin, mode = Pin.IN, pull=Pin.PULL_UP)
        '''Initializes the output Pin for a bump sensor'''

    def check(self) -> bool:
        '''Checks if the bump sensor is pressed

        :return: `False` if the bump sensor was pressed, `True` otherwise
        :rtype: bool
        '''
        return self.digital_pin.value()
    

class ButtonArray:
    '''Button Sensor Array'''

    def __init__(self, button_list:list[Pin]):
        '''Initializes a Button Sensor Array Object 

        :param button_list: List of digital pins for an array of bump sensors
        '''
        
        self.sensor_list = [ButtonSensor]*len(button_list)
        '''List of button sensors in the array'''

        for idx,sensor in enumerate(button_list):
            self.sensor_list[idx] = ButtonSensor(sensor)
        '''Creates a ButtonSensor object for each pin in the button_list'''    

    def read_all(self) -> bool:
        '''read all bump sensors in the array

        :return: `False` if just one bump sensor in the array was pressed,
            `True` otherwise
        :rtype: bool
        '''
        for sensor in self.sensor_list:
            if not sensor.check():
                return False
        return True
    

if __name__ == "__main__":
    buttons = [(Pin.cpu.B12),
               (Pin.cpu.B11),
               (Pin.cpu.B2),
               (Pin.cpu.A10),
               (Pin.cpu.B3),
               (Pin.cpu.B10)]
    
    button_sensors = ButtonArray(buttons)

    while True:
        delay(100)
        print(button_sensors.read_all())

