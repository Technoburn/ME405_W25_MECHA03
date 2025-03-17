Tasks
=====

Our program uses a multitasking task-state paradigm, making use of the 
`ME405 Library <https://spluttflob.github.io/ME405-Support/index.html>`_ provided
scheduler and `Shares` which allows for scheduled execution of generator
functions which implement finite state machines with variables shared between 
tasks as necessary.

Task Structure
--------------

.. image:: ../_static/TaskDiagram.png
   :width: 100%
   :alt: Task Diagram

Overall 7 Tasks are implemented: 

The "Course" Task keeps track of which segement of the course ROMI is in, 
taking in feedback data from the sensors, operating control loops, and sending 
setpoint velocities to the 2 motors.

The 2 "Motor" Tasks implement closed loop velocity control on each motor 
individually, using feedback from the respective encoder.

The "Bump" Task interfaces with the bump sensors, raising a flag if a bump 
occurs.

The "IMU" Task handles the calibration of the IMU and outputs heading and yaw 
rate feedback.

The "Line Sensor" Task handles the calibration of the Line Sensor Array and 
outputs centroid feedback.

Shares
------

.. list-table::
    :widths: 30 20 70
    :header-rows: 1

    * - Variable
      - Data Type
      - Purpose
    * - run
      - Unsigned Byte
      - Flag to signal when ROMI should begin running the course
    * - bump
      - Unsigned Byte
      - Flag to signal when a bump has occured
    * - cal_white
      - Unsigned Byte
      - Flag to tell line sensor to use value for white calibration
    * - cal_black
      - Unsigned Byte
      - Flag to tell line sensor to use value for black calibration
    * - sys
      - Unsigned Byte
      - Flag for IMU System Calibration Status
    * - gyro
      - Unsigned Byte
      - Flag for IMU Gyro Calibration Status
    * - acc
      - Unsigned Byte
      - Flag for IMU Accelerometer Calibration Status
    * - mag
      - Unsigned Byte
      - Flag for IMU Magnetometer Calibration Status
    * - enc_reset_L
      - Unsigned Byte
      - Flag to tell left encoder to reset position
    * - enc_reset_R
      - Unsigned Byte
      - Flag to tell left encoder to reset position
    * - centroid
      - Float
      - Centroid feedback value from Line Sensor Array
    * - heading
      - Float
      - Heading feedback value from IMU
    * - yaw_rate
      - Float
      - Yaw Rate feedback value from IMU
    * - Omega_L
      - Float
      - Left Motor angular velocity setpoint
    * - Omega_R
      - Float
      - Right Motor angular velocity setpoint
    * - theta_L
      - Float
      - Left Motor angular position feedback value from encoder
    * - theta_R
      - Float
      - Right Motor angular position feedback value from encoder

Task Profile
------------

.. list-table::
    :header-rows: 1

    * - TASK
      - PRI
      - PERIOD
      - RUNS
      - AVG DUR
      - MAX DUR
      - AVG LATE
      - MAX LATE
    * - Task Left Motor
      - 1
      - 5.0
      - 1064
      - 0.237
      - 1.454
      - 0.958
      - 9.871