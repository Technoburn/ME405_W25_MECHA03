class Path:
    '''Implement Custom Data Structure for running defined paths'''

    WAIT = 0
    LINE = 1
    TURN = 2

    OFF = 0
    ERR = 1
    NXT = 2

    def __init__(self,type:int,s:float,v:float,datum:float,rel_angle:float,
                 follow:bool,compass:bool,bump_mode:int):
        '''
        Initializes Path Object

        :param type: Path Type (LINE or TURN)
        :param s: Path Length [mm]
        :param v: Path Longitudinal Velocity [mm/s]
        :param datum: Datum Heading [deg]
        :param rel_angle: Path Heading Relative to starting heading [deg]
        :param follow: Boolean to specify whether to Line Follow
        :param compass: Boolean to specify whether to Compass Track 
        :param bump: Bump mode (Off, Error, or Next State)    
        '''

        self.type = type
        self.s = s
        self.v = v
        self.heading = datum + rel_angle
        self.follow = follow
        self.compass = compass
        self.bump_mode = bump_mode