from micropython import const
from pyb import I2C,delay
import struct

class BNO055:
    '''A BNO055 IMU interface encapsulated in a Python class'''

    DEV_ADDR = 0x28
    '''I2C Peripheral Address for the IMU'''

    class reg:
        '''BNO055 Used Register Map'''

        CALIB_DATA    = (const(0x55), b"b"*22)
        OPR_MODE      = (const(0x3D), b"b")
        CALIB_STAT    = (const(0x35), b"b")
        EUL_DATA_ALL  = (const(0x1A), b"<hhh")
        EUL_HEADING   = (const(0x1A), b"<h")
        GYRO_DATA_ALL = (const(0x14), b"<hhh")
        GYRO_YAW_RATE = (const(0x18), b"<h")

    class mode:
        '''BNO055 Modes'''

        CONFIGMODE   = 0b0000_0000
        # Non-fusion Modes
        ACCONLY      = 0b0000_0001
        MAGONLY      = 0b0000_0010
        GYROONLY     = 0b0000_0011
        ACCMAG       = 0b0000_0100
        ACCGYRO      = 0b0000_0101
        MAGGYRO      = 0b0000_0110
        AMG          = 0b0000_0111
        # Fusion modes
        IMU          = 0b0000_1000
        COMPASS      = 0b0000_1001
        M4G          = 0b0000_1010
        NDOF_FMC_OFF = 0b0000_1011
        NDOF         = 0b0000_1100

    def __init__(self, i2c:I2C):
        '''Initializes BNO055 object

        :param i2c: I2C object preconfigured in CONTROLLER mode
        '''
        self._i2c = i2c

        self._buf = bytearray(22)

        self._cal_data = self._buf

    def _write_reg(self,reg,value:bytearray):
        '''Write a byte array to a given memory register
        
        :param reg: Register within the reg class for BNO055
        :param value: Byte array of the value to be writen to the register
        '''
        self._i2c.mem_write(value, BNO055.DEV_ADDR, reg[0])

    def _read_reg(self,reg) -> tuple:
        '''Read a specific memory register value
        
        :param reg: Register within the reg class for BNO055
        :return: tuple of values inside desired register
        :rtype: tuple
        '''
        # Determine number of bytes to read
        length = struct.calcsize(reg[1])

        # Create memoryview object of the right size
        buf = memoryview(self._buf)[:length]

        # Read from the I2C bus into memoryview
        self._i2c.mem_read(buf, BNO055.DEV_ADDR, reg[0])

        return struct.unpack_from(reg[1], buf)

    def _set_mode(self, mode):
        '''Change operating mode of IMU
        
        :param mode: desired mode of the IMU witin the mode class
        '''

        # Write xxxx1100b to OPR_MODE Register
        self._write_reg(BNO055.reg.OPR_MODE, mode)

    def get_status(self) -> tuple[bool,bool,bool,bool]:
        '''Retrieve and parse the calibration status byte from the IMU

        :return sys, gyro, acc, mag: A tuple of bools that will be `True` if 
            a corresponding sensor is calibrated. 
        '''

        self._set_mode(BNO055.mode.NDOF) # Switch to NDOF mode

        # Read CALIB_STAT Register
        cal_status, = self._read_reg(BNO055.reg.CALIB_STAT)

        sys = (cal_status >> 6) & 3
        gyro = (cal_status >> 4) & 3
        acc = (cal_status >> 2) & 3
        mag = cal_status & 3

        # Return true if all sensors are calibrated
        return sys == 3, gyro == 3, acc == 3, mag == 3
    
    def read_calibration(self) -> bytearray:
        '''Retrieve the calibration coefficients from the IMU as a binary
        data and writes it to calibration.txt
        
        :return cal_data: Calibration Coefficients from registers 
            at memory address 0x55-0x6A
        '''

        self._set_mode(BNO055.mode.CONFIGMODE) # Set operation mode to CONFIGMODE

        # Read Calibration Coefficients from registers at memaddr 0x55-0x6A
        cal_data = bytearray(self._read_reg(BNO055.reg.CALIB_DATA))

        self._set_mode(BNO055.mode.NDOF) # Return to operation mode NDOF

        # Write calibration data to file
        with open("calibration.txt","wb") as file:
            file.write(cal_data)

        return cal_data

    def write_calibration(self) -> bytearray:
        '''write calibration coefficients back to the IMU from pre-recorded
        binary data in calibration.txt
        
        :return cal_data: Calibration Coefficients from registers 
            at memory address 0x55-0x6A
        '''

        # Read calibration data from file
        with open("calibration.txt","rb") as file:
            cal_data = bytearray(file.read(len(self._cal_data)))

        self._set_mode(BNO055.mode.CONFIGMODE) # Set operation mode to CONFIGMODE

        # Write Calibration Coefficients to registers at memaddr 0x55-0x6A
        self._write_reg(BNO055.reg.CALIB_DATA, cal_data)

        self._set_mode(BNO055.mode.NDOF) # Return to operation mode NDOF

        return cal_data
    
    def get_value(self,reg):
        '''read IMU data from the reg class. Includes Euler angles and headings
        
        :param reg: Register within the reg class for BNO055
        :return: Tuple from desired register
        :rtype: Tuple        
        '''

        self._set_mode(BNO055.mode.NDOF)

        return self._read_reg(reg)
    
    def angle_diff(self,angle1:int,angle2:int) -> float:
        '''Computes the angle difference angle1-angle2 such that the value is
        between -180 and 180

        :param angle1: First angle in degrees
        :param angle2: Second angle in degrees
        :return: Float of the difference of the two angles between -180 
            and +180 degrees    
        :rtype: float    
        '''

        # Caluclate the difference between the angles
        angle = angle1 - angle2

        # If the angle has a magnitude greater than 180 offset the angle by 360
        if abs(angle) > 180:
            angle += 360

        return angle
    
if __name__ == "__main__":
    controller = I2C(2,I2C.CONTROLLER)

    imu = BNO055(controller)

    delay(1000)

    try:
        print(f"Written Data:\n{imu.write_calibration()}") # Print written data

    except OSError:
        print("Calibration File Not Found, Perform Calibration")

        # Wait for Calibration to complete
        while not all(imu.get_status()):
            print(imu.get_status())
            delay(100)

        # Retrieve calibration data from IMU
        print(f"Saved Data: \n{imu.read_calibration()}")
        delay(100)

        delay(100)
        print(f"Calibrated = {imu.get_status()}")