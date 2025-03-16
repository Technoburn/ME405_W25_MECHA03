from time import ticks_us,ticks_diff

class ClosedLoop:
    '''Implement Closed-loop Control (PID) with Feed Forward for a given system
    '''

    def __init__(self,KP:float,KI=0.,KD=0.,KFF=0.):
        '''
        Initializes Closed-loop Controller Object
        
        :param KP: Proportional Controller Gain
        :param KI: Integral Controller Gain
        :param KD: Derivative Controller Gain
        :param KFF: Feed Forward Gain
        '''

        self.KP = KP
        '''Proportional Controller Gain'''
        self.KI = KI
        '''Integral Controller Gain'''
        self.KD = KD
        '''Derivative Controller Gain'''
        self.KFF = KFF
        '''Feed Forward Gain'''
        self.prev_err = 0
        '''Previous error in consistent units'''
        self.integral_err = 0
        '''Integral of error in consistent units'''
        self.prev_ticks = ticks_us()
        '''Previous time (us)'''

    def reset(self):
        '''Reset error values for clean initial start-up
        '''
        self.prev_err = 0
        self.integral_err = 0
        self.prev_ticks = ticks_us()

    def controller(self,setpoint,feedback,feedforward=0.) -> tuple:
        '''
        Run 1 loop of closed-loop feedback PID controller with given setpoint
        and feedback, assume consistent units

        :param setpoint: Setpoint value for controller
        :param feedback: Feedback value for controller
        :param feedforward: Feedforward value for controller

        :return P_power,I_power,D_power,F_power:
            Outputs for Proportional, Integral, Derivative, and Feedforward
            controllers      
        '''

        error = setpoint-feedback
        current_ticks = ticks_us()
        dt = ticks_diff(current_ticks,self.prev_ticks)

        # Proportional Controller
        P_power = self.KP*error

        # Integral Controller
        self.integral_err += (error*dt)*1e-6
        I_power = self.KI*self.integral_err

        # Derivative Controller
        derivative_err = ((error - self.prev_err)*1e+6)/dt
        D_power = self.KD*derivative_err

        # Feed Forward Controller
        F_power = self.KFF*feedforward

        # Set previous values to current values
        self.prev_err = error
        self.prev_ticks = current_ticks

        return (P_power,I_power,D_power,F_power)