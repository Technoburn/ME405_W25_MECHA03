from motor import Motor
from encoder import Encoder
from controller import ClosedLoop
from voltage import Voltage
from task_share import Share

class Task_Motor:
    def __init__(self,Omega:Share,enc_reset:Share,theta:Share,
                 motor:Motor,enc:Encoder,PID:ClosedLoop,batt:Voltage):
        '''The `Task_Motor` task manages motor control using a closed-loop PID 
        controller. It continuously updates encoder readings, shares wheel 
        position, and calculates actuation voltage based on the motor's 
        velocity setpoint. The actuation voltage is converted into a PWM 
        effort percentage, considering the current battery voltage.

        :param Omega: A `share` of the desired motor velocity in rad/s.
        :param enc_reset: A `share` that signals when to reset the encoder.
        :param motor: A `Motor` object to be controlled
        :param enc: A `Encoder` object, providing position and velocity 
            feedback.
        :param PID: A `ClosedLoop` controller object that computes the 
            necessary PWM to achieve the desired motor velocity.
        :param batt: A `Voltage` object that reads the current battery voltage.

        :return theta: A `share` of the calculated wheel position in radians.
        '''
        
        # Copy parameters to properties
        self.Omega = Omega
        self.enc_reset = enc_reset
        self.theta = theta
        self.motor = motor
        self.enc = enc
        self.PID = PID
        self.batt = batt

        # States of the FSM
        self.S0_RUN = 0

        # Preinitialization
        # This code before the loop initializes the Python code and structure of
        # FSM but does not initialize the FSM itself
        self.PID.reset() # Reset PID Error values
        self.bat_volt = self.batt.read_voltage() # Get Battery Voltage
        self.state = self.S0_RUN

    def task(self):

        while True:
            if self.state == self.S0_RUN:
                self.motor.enable()

                # Reset encoder as directed
                if self.enc_reset.get():
                    self.enc.zero()
                    self.enc_reset.put(False)

                # Update Encoder
                self.enc.update()

                # Share wheel position
                self.theta.put((self.enc.get_position()*2*3.14)/1440)

                # Get motor velocity setpoint
                Omega_set = self.Omega.get()

                # Determine actual motor velocity in rad/s
                Omega_act = (self.enc.get_velocity()*2*3.14*1_000_000)/1440

                # Run controller to determine motor actuation voltage
                act_voltage = self.PID.controller(Omega_set,Omega_act,Omega_set)

                # Calculate effort required for actuation voltage
                act_efft = (sum(act_voltage)+self.motor.Startup_V)*100/self.bat_volt

                # Set actuation effort
                self.motor.set_effort(act_efft)

            else:
                raise ValueError("Invalid State")
            
            yield self.state