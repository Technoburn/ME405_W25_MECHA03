from pyb import Pin,ADC

class Voltage:

    '''A ADC pin to read the voltage of the batterys'''

    def __init__(self, adc_Pin:Pin):
        ''' Initializes a voltage sensor object
        :param adc_Pin: Analog input pin to read voltage
        '''
    
        self.adc = ADC(adc_Pin)
        '''Voltage Sensor ADC Object'''

    def read_voltage(self):
        '''Reads and returns the calculated voltage of the batteries

        :return voltage: Adjusted voltage from the battery to account for 
            voltage divider
        '''
        #has to adjust for voltage divider
        voltage = self.adc.read()*3.12/4095*3

        return voltage
    

if __name__ == "__main__":
    while True:
        voltage_sensor = Voltage(Pin.cpu.B1)

        input("Press enter to read voltage of Romi")
        voltage_reading = voltage_sensor.read_voltage()

        print(voltage_reading)