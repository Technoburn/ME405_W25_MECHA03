from time import ticks_us,ticks_diff
from controller import ClosedLoop
from path import Path
from task_share import Share

class Task_Course:
    def __init__(self,run:Share,Omega_L:Share,Omega_R:Share,heading:Share,
                 yaw_rate:Share,centroid:Share,bump:Share,enc_reset_L:Share,
                 enc_reset_R:Share,theta_L:Share,theta_R:Share):
        '''The `Task_Course` task guides ROMI through a predefined course using 
        a list of `Path` objects. Each path segment specifies the desired 
        velocity, heading, yaw rate, and whether ROMI should follow a line or a 
        compass heading. It uses PID controllers to adjust ROMI's movement.
        
        :param run: A `share` that signals the task to start running the 
            course.
        :param Omega_L: A `share` of angular velocity of the left wheel in 
            rad/s.
        :param Omega_R: A `share` of angular velocity of the right wheel in 
            rad/s.
        :param heading: A `share` of the current heading angle of the robot 
            in degrees.
        :param yaw_rate: A `share` of the measured yaw rate of the robot in 
            rad/s.
        :param centroid: A `share` of the detected position of the line.
        :param bump: A `share` of indicating whether a collision been detected.
        :param enc_reset_L: A `share` to reset the left encoder count.
        :param enc_reset_R: A `share` to reset the right encoder count.
        :param theta_L: A `share` of the cumulative angle measured by the 
            left wheel encoder.
        :param theta_R: A `share` of the cumulative angle measured by the 
            right wheel encoder.
            
        '''
        
        # Copy parameters to properties
        self.run = run
        self.Omega_L = Omega_L
        self.Omega_R = Omega_R
        self.heading = heading
        self.yaw_rate = yaw_rate
        self.centroid = centroid
        self.bump = bump
        self.enc_reset_L = enc_reset_L
        self.enc_reset_R = enc_reset_R
        self.theta_L = theta_L
        self.theta_R = theta_R

        # States of the FSM
        self.S0_WAIT = 0
        self.S1_LINE = 1
        self.S2_TURN = 2

        # Preinitialization
        # This code before the loop initializes the Python code and structure of
        # FSM but does not initialize the FSM itself
        self.line_PID = ClosedLoop(1,1e-8) # Create Line Follow PID
        self.compass_PID = ClosedLoop(0.15,1.5e-6) # Create Compass PID
        self.yaw_PID = ClosedLoop(0.2,5e-6,KFF=1) # Creat Yaw Rate PID
        self.state = self.S0_WAIT

    def task(self):
        '''Generator Function to run implemented Finite-State Machine'''

        while True:
            if self.state == self.S0_WAIT:
                # Set wheel angular velocity to 0
                self.Omega_L.put(0)
                self.Omega_R.put(0)

                if self.run.get():
                    # Reset PID Error values
                    self.line_PID.reset()
                    self.compass_PID.reset()
                    self.yaw_PID.reset()

                    # Reset Encoder Positions
                    self.enc_reset_L.put(True) 
                    self.enc_reset_R.put(True)
                    s = 0

                    self.run.put(False)

                    fwd_angle = self.heading.get()

                    v_set = 800

                    LF380 = Path(Path.LINE,380,v_set,0,0,True,False,Path.ERR)
                    ENC540 = Path(Path.LINE,540,v_set,fwd_angle,-35,False,True,
                                  Path.ERR)
                    ENC520 = Path(Path.LINE,520,v_set,fwd_angle,37.5,False,True,
                                  Path.ERR)
                    ENC570 = Path(Path.LINE,570,v_set,fwd_angle,-90,False,True,
                                  Path.OFF)
                    ENC150 = Path(Path.LINE,150,v_set,fwd_angle,-180,False,True,
                                 Path.OFF)
                    LF540 = Path(Path.LINE,540,v_set,0,0,True,False,Path.ERR)
                    ENC600 = Path(Path.LINE,600,v_set,fwd_angle,-180,False,True,
                                  Path.ERR)
                    ENC151 = Path(Path.LINE,151,v_set,fwd_angle,90,False,True,
                                  Path.OFF)
                    LF220 = Path(Path.LINE,220,v_set,0,0,True,False,Path.OFF)
                    ENCTB = Path(Path.LINE,1000,300,fwd_angle,90,False,True,
                                 Path.NXT)
                    REV245 = Path(Path.LINE,245,-v_set,fwd_angle,-180,False,True,
                                  Path.OFF)
                    REV250 = Path(Path.LINE,250,-v_set,fwd_angle,-60,False,True,
                                  Path.ERR)
                    REV225 = Path(Path.LINE,225,-v_set,fwd_angle,0,False,True,
                                  Path.ERR)
                    END = Path(Path.WAIT,0,0,0,0,False,False,Path.ERR)

                    full_path = [LF380,
                                 ENC540,
                                 ENC520,
                                 ENC570,
                                 ENC150,
                                 LF540,
                                 ENC600,
                                 ENC151,
                                 LF220,
                                 ENCTB,
                                 REV245,
                                 REV250,
                                 REV225,
                                 END]

                    path_idx = 0

                    self.state = full_path[path_idx].type

            elif self.state == self.S1_LINE:
                # Calculate Distance traveled by Romi
                s = 35*(self.theta_L.get() + self.theta_R.get())/2

                # Bump Detection
                if not self.bump.get():
                    if full_path[path_idx].bump_mode == Path.ERR:
                        raise ValueError("Bump Detected") # Error out
                    elif full_path[path_idx].bump_mode == Path.NXT:
                        s = full_path[path_idx].s

                if abs(s) < full_path[path_idx].s:

                    # Longitudinal velocity setpoint [mm/s]
                    v_set = full_path[path_idx].v

                    # Heading setpoint [degs]
                    heading_set = full_path[path_idx].heading

                    # Yaw Rate setpoint [rad/s]
                    if full_path[path_idx].compass:
                        
                        if (heading_set - self.heading.get()) >= 180:
                            heading_set -= 360
                            full_path[path_idx].heading = heading_set
                        elif (heading_set - self.heading.get()) <= -180:
                            heading_set += 360
                            full_path[path_idx].heading = heading_set

                        Omega_set = sum(self.compass_PID.controller(heading_set,
                                                        self.heading.get()))
                    
                    elif full_path[path_idx].follow:
                        Omega_set = sum(self.line_PID.controller(7,
                                                        self.centroid.get()))
                    
                    else:
                        Omega_set = 0

                    Omega_c = sum(self.yaw_PID.controller(Omega_set,
                                                            self.yaw_rate.get(),
                                                            Omega_set))

                    # Left and Right Angular Velocity Setpoint [rad/s]
                    self.Omega_L.put((v_set - (141*Omega_c)/2)/35)
                    self.Omega_R.put((v_set + (141*Omega_c)/2)/35)

                else:
                    # Reset Encoder Positions
                    self.enc_reset_L.put(True) 
                    self.enc_reset_R.put(True)
                    s = 0

                    # Reset PID Error
                    self.line_PID.reset()
                    self.compass_PID.reset()
                    self.yaw_PID.reset()

                    path_idx += 1

                    self.state = full_path[path_idx].type

            elif self.state == self.S2_TURN:
                # Bump Detection
                if not self.bump.get():
                    if full_path[path_idx].bump_mode == Path.ERR:
                        raise ValueError("Bump Detected") # Error out

                v_set = 0 # Longitudinal velocity setpoint [mm/s]

                # Heading setpoint [degs]
                heading_set = full_path[path_idx].heading

                if (heading_set - self.heading.get()) >= 180:
                            heading_set -= 360
                            full_path[path_idx].heading = heading_set
                elif (heading_set - self.heading.get()) <= -180:
                    heading_set += 360
                    full_path[path_idx].heading = heading_set

                # Yaw Rate setpoint [rad/s]
                Omega_set = sum(self.compass_PID.controller(heading_set,
                                                        self.heading.get()))

                Omega_c = sum(self.yaw_PID.controller(Omega_set,
                                                        self.yaw_rate.get(),
                                                        Omega_set))

                # Left and Right Angular Velocity Setpoint [rad/s]
                self.Omega_L.put((v_set - (141*Omega_c)/2)/35)
                self.Omega_R.put((v_set + (141*Omega_c)/2)/35)

                if abs((heading_set) - self.heading.get()) < 2:
                    # Reset Encoder Positions
                    self.enc_reset_L.put(True) 
                    self.enc_reset_R.put(True)
                    s = 0

                    # Reset PID Error
                    self.line_PID.reset()
                    self.compass_PID.reset()
                    self.yaw_PID.reset()

                    path_idx += 1

                    self.state = full_path[path_idx].type           

            else:
                raise ValueError("Invalid State")
            
            yield self.state