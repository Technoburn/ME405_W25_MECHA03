from array import array
from time import ticks_ms,ticks_us,ticks_add,ticks_diff
from encoder import Encoder
from pyb import Pin

class Collector:
    '''Collect encoder data'''

    def __init__(self, enc:Encoder):
        '''Initializes Collector Object'''
        
        self.enc = enc
        self.start = ticks_ms()

        self.t_buf = array('H',(0 for n in range(1000)))
        self.p_buf = array('l',(0 for n in range(1000)))
        self.v_buf = array('f',(0 for n in range(1000)))
        self.idx   = 0

    def collect(self):
        self.enc.update()

        self.t_buf[self.idx] = ticks_diff(ticks_ms(),self.start)
        self.p_buf[self.idx] = self.enc.get_position()
        self.v_buf[self.idx] = self.enc.get_velocity()

        self.idx += 1

if __name__ == "__main__":

    interval = 10_000 # Time interval (us)

    # Create encoder object as instance of encoder class
    ENC = Encoder(3,Pin.cpu.B5,Pin.cpu.B4)

    data = Collector(ENC) # Create collector object

    start = ticks_us() # Time of 1st run

    deadline = ticks_add(start, interval) # first run deadline

    ENC.zero()
    while data.idx < 1000:

        now = ticks_us() # Current time (us)

        # Check if deadline elapsed
        if ticks_diff(deadline,now) <= 0:
            # Collect instance of data
            data.collect()
            deadline = ticks_add(now, interval) # Prep next deadline

    for index,value in enumerate(data.t_buf):
        print(f"{data.t_buf[index]},{data.p_buf[index]},{data.v_buf[index]}")