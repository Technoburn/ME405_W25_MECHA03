from pyb import Pin,Timer

class Motor:
    '''A motor driver interface encapsulated in a Python class. Works with 
    motor drivers using separate PWM and direction inputs such as the DRV8838
    drivers present on the Romi chassis from Pololu.'''

    def __init__(self, PWM:tuple[Timer,int,Pin], DIR:Pin, nSLP:Pin,startup:int):
        '''Initializes a Motor object

        :param PWM: Information required to set up PWM pin (Timer,channel_num,
            Pin)
        :param DIR: Direction Pin
        :param nSLP: not Sleep Pin
        :param startup: Start up voltage for the motor
        '''
        
        # Validate 1st value of PWM as indicating Channel 1,2,3,4
        if PWM[1] not in {1,2,3,4}:
            raise ValueError("Must define a timer channel between 1 and 4")

        self.nSLP_pin = Pin(nSLP, mode = Pin.OUT_PP)
        '''Motor driver NOT sleep (Enable) Pin'''
        self.DIR_pin = Pin(DIR, mode=Pin.OUT_PP)
        '''Motor driver direction pin'''
        self.PWM_pin = PWM[0].channel(PWM[1],pin=PWM[2],mode=Timer.PWM,
                                      pulse_width_percent=0)
        '''Motor driver PWM TimerChannel object'''
        self.Startup_V = startup
        '''Motor start up voltage'''

    def set_effort(self, effort:int):
        '''Sets the present effort for a motor object

        :param effort: Integer between -100 and 100, the percent effort to the 
            motor    
        '''
        
        # Switch direction pins to match direction of signed input
        if effort < 0:
            self.DIR_pin.high() # High -> Backwards
        else:
            self.DIR_pin.low() # Low -> forwards

        # Set pulse width to match magnitude of desired effort
        self.PWM_pin.pulse_width_percent(abs(effort))

    def enable(self):
        '''Enables the motor by taking it out of sleep mode, into brake
        mode'''
        self.nSLP_pin.high()

    def disable(self):
        '''Disables the motor driver by taking it into sleep mode'''
        self.nSLP_pin.low()

if __name__ == "__main__":
    # Create motor PWM timer object
    motor_PWM = Timer(4,freq=1000)

    # Create left motor object as instance of motor class
    left_motor = Motor((motor_PWM,2,Pin.cpu.B7),Pin.cpu.D2,Pin.cpu.C11)

    # Create right motor object as instance of motor class
    right_motor = Motor((motor_PWM,4,Pin.cpu.B9),Pin.cpu.B8,Pin.cpu.C9)    

    left_motor.enable()
    right_motor.enable()

    left_motor.set_effort(10.5) # Test if non-Int input is accepted

    while True:
        # Take user desired motor effort input
        inputPrompt = input("Desired Motor Effort % (L,R): ")

        # Split the response into left and right
        desiredEffort = inputPrompt.split(",")
        
        left_motor.set_effort(int(desiredEffort[0]))
        right_motor.set_effort(int(desiredEffort[1]))