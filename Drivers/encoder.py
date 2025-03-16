from pyb import Pin, Timer
import time, math

class Encoder:
    '''A quadrature encoder decoding interface encapsulated in a Python class'''

    def __init__(self, tim:int, chA_pin:Pin, chB_pin:Pin):
        ''' Initializes an Encoder Object

            :param tim: Timer number for encoder
            :param chA_pin: Channel A Pin
            :param chB_pin: Channel B Pin
        '''
        
        #set up timer pin
        self.ENC = Timer(tim, period = 0xFFFF, prescaler = 0)
        '''Encoder Timer Object'''
        self.ChA_pin = self.ENC.channel(1, pin=chA_pin, mode=Timer.ENC_AB)
        '''Encoder channel A timer channel in ENC_AB mode'''
        self.ChB_pin = self.ENC.channel(2, pin=chB_pin, mode=Timer.ENC_AB)
        '''Encoder channel B timer channel in ENC_AB mode'''
        self.position = 0
        '''Total accumulated position of the encoder'''
        self.prev_count = self.ENC.counter()
        '''Timer Counter from the previous update'''
        self.prev_time = time.ticks_us()
        '''Ticks from most recent update'''
        self.delta = 0
        '''Change in count between last two updates'''
        self.dt = 0
        '''Amount of time between last two updates'''

    def update(self):
        '''Runs one update step on the encoder's timer counter to keep
        track of the change in count and check for counter reload
        '''
        #set the current count as the Encoder Count
        current_count = self.ENC.counter()
        #get differance of counter
        self.delta = current_count - self.prev_count
        
        # Checks for over/underflow
        # If magnitude larger that the auto reload plus 1 /2
        if abs(self.delta) > (0xFFFF + 1) / 2:
            if self.delta > 0:
                self.delta -= (0xFFFF + 1)
            else:
                self.delta += (0xFFFF + 1)

        # Update position with count change between last 2 updates
        self.position += self.delta

        # Sets current count as the new previous count
        self.prev_count = current_count

        # Get change in time between last 2 updates
        now = time.ticks_us()
        self.dt = time.ticks_diff(now,self.prev_time)
        self.prev_time = now

    def get_position(self) -> int:
        '''Returns the most recently updated value of position as determined
        within the update() method
        
        :return position: Integer of most recent position of encoder 
        '''
        return self.position

    def get_velocity(self) -> float:
        '''Returns a measure of velocity using the most recently updated
        value of delta as determined within the update() method
        
        :return delta/dt: Float of most recent encoder velocity
        '''
        return self.delta/self.dt

    def zero(self):
        '''Sets the present encoder position to zero
        '''
        self.position = 0
        self.prev_count = self.ENC.counter()

if __name__ == "__main__":
    # Create left encoder object as instance of encoder class
    left_enc = Encoder(3,Pin.cpu.B5,Pin.cpu.B4)

    # Create right encoder object as instance of encoder class
    right_enc = Encoder(1,Pin.cpu.A9,Pin.cpu.A8)

    left_enc.zero()
    right_enc.zero()
        
    while True:
        left_enc.update()
        right_enc.update()

        print(left_enc.get_position(),
              left_enc.get_velocity(),
              right_enc.get_position(),
              right_enc.get_velocity())