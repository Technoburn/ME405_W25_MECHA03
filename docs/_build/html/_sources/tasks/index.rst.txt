Tasks
=====

Task Structure
--------------

// Insert Task Diagram Pic

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
    