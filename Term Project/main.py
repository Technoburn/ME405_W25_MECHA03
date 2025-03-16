# Multitasking
import cotask
from task_share import Share

# Drivers
from pyb import Timer,Pin,I2C
from voltage import Voltage
from motor import Motor
from encoder import Encoder
from controller import ClosedLoop
from line_sensor import SensorArray
from button import ButtonArray
from imu import BNO055

# Tasks
from task_repl import Task_Repl
from task_motor import Task_Motor
from task_course import Task_Course
from task_line_sensors import Task_Line_Sensor
from task_imu import Task_IMU
from task_button import Task_Button

# Garbage Collection
from gc import collect
collect()

# Create motor PWM timer object
motor_PWM = Timer(4,freq=20000)

# Create Battery Voltage Monitor
batt = Voltage(Pin.cpu.B1)

# Create left motor, encoder, controller
left_motor = Motor((motor_PWM,2,Pin.cpu.B7),Pin.cpu.D2,
                    Pin.cpu.C12,0.10)
left_enc = Encoder(3,Pin.cpu.B5,Pin.cpu.B4)
left_PID = ClosedLoop(2,0.01,KFF=1/4.24)

# Create right motor, encoder, controller
right_motor = Motor((motor_PWM,4,Pin.cpu.B9),Pin.cpu.B8,
                    Pin.cpu.C9,0.01)
right_enc = Encoder(1,Pin.cpu.A9,Pin.cpu.A8)
right_PID = ClosedLoop(2,0.01,KFF=1/3.78)

# Create controller and imu
controller = I2C(2,I2C.CONTROLLER)
imu = BNO055(controller)

# Create line sensors
sensors_defined = [(Pin.cpu.A1,1),
                    (Pin.cpu.C2,2),
                    (Pin.cpu.A0,3),
                    (Pin.cpu.C3,4),
                    (Pin.cpu.A6,5),
                    (Pin.cpu.C0,6),
                    (Pin.cpu.A7,7),
                    (Pin.cpu.C1,8),
                    (Pin.cpu.C5,9),
                    (Pin.cpu.B0,10),
                    (Pin.cpu.C4,11),
                    (Pin.cpu.A4,12)]                  

line_sensors = SensorArray(Pin.cpu.H0, sensors_defined)
line_sensors.CNTRL.low() # Turn off emmitters

# Create Bump Sensors
bump_sensors = ButtonArray([(Pin.cpu.B12),(Pin.cpu.B11),(Pin.cpu.B2),
                            (Pin.cpu.A10),(Pin.cpu.B3),(Pin.cpu.B10)])

# Create Shares & Queues
# Flags
run = Share('B', name="Run Flag")
bump = Share('B', name="Bumb Flag")
cal_white = Share('B', name="Calibrate White Flag")
cal_black = Share('B', name="Calibrate Black Flag")
sys = Share('B', name="System Calibration Status")
gyro = Share('B', name="Gyro Calibration Status")
acc = Share('B', name="Accelerometer Calibration Status")
mag = Share('B', name="Magnetometer Calibration Status")
enc_reset_L = Share('B', name="Left Encoder Reset Flag")
enc_reset_R = Share('B', name="Right Encoder Reset Flag")

# Feedback
centroid = Share('f', name="Centroid")
heading = Share('f', name="Heading")
yaw_rate = Share('f',name="Yaw Rate")
Omega_L = Share('f', name="Left Angular Velocity Setpoint")
Omega_R = Share('f', name="Right Angular Velocity Setpoint")
theta_L = Share('f',name="Left Angular Position")
theta_R = Share('f',name="Right Angular Position")

# Create task class instances
class_L_motor = Task_Motor(Omega_L,enc_reset_L,theta_L,
                           left_motor,left_enc,left_PID,batt)
class_R_motor = Task_Motor(Omega_R,enc_reset_R,theta_R,
                           right_motor,right_enc,right_PID,batt)
class_Course = Task_Course(run,Omega_L,Omega_R,heading,yaw_rate,centroid,bump,
                           enc_reset_L,enc_reset_R,theta_L,theta_R)
class_IMU = Task_IMU(sys,gyro,acc,mag,heading,yaw_rate,imu)
class_Line_Sensor = Task_Line_Sensor(cal_white,cal_black,centroid,line_sensors)
class_Bump = Task_Button(bump,bump_sensors)
class_BT_REPL = Task_Repl(sys,gyro,acc,mag,run,cal_white,cal_black)

# Create tasks
task_L_Motor = cotask.Task(class_L_motor.task, name="Task Left Motor",
                           priority=4,period=7,profile=True)
task_R_Motor = cotask.Task(class_R_motor.task, name="Task Right Motor",
                           priority=4,period=7,profile=True)
task_Course = cotask.Task(class_Course.task, name="Task Course",
                          priority=3,period=12,profile=True)
task_IMU = cotask.Task(class_IMU.task,name="Task IMU",
                        priority=2,period=20,profile=True)
task_Line_Sensors = cotask.Task(class_Line_Sensor.task,name="Task Line Sensors",
                                priority=2,period=22,profile=True)
task_Bump = cotask.Task(class_Bump.task, name="Task Bump",
                        priority=1,period=28,profile=True)
task_BT_REPL = cotask.Task(class_BT_REPL.task, name="Task BT REPL",
                           priority=0,period=50,profile=True)

# Append tasks to task list
cotask.task_list.append(task_L_Motor)
cotask.task_list.append(task_R_Motor)
cotask.task_list.append(task_Course)
cotask.task_list.append(task_IMU)
cotask.task_list.append(task_Line_Sensors)
cotask.task_list.append(task_Bump)
cotask.task_list.append(task_BT_REPL)

if __name__ == "__main__":
    while True:
        try:
            # Run one cycle of the task
            cotask.task_list.pri_sched()
        
        except KeyboardInterrupt:
            # Disable Motors
            left_motor.disable()
            right_motor.disable()

            print("Program Terminated")

            # Print a table of task data and a table of shared information data
            print('\n' + str (cotask.task_list))
            print('')
            break

        except:
            # Disable Motors
            left_motor.disable()
            right_motor.disable()

            # Raise error again
            raise