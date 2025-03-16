Boot
====

The boot script executes on startup and ensures that specific pins are 
configured properly and the Bluetooth serial device is operational.

.. code-block:: python
    
    from pyb import UART, Pin
    from pyb import repl_uart

    PC9 = Pin(Pin.cpu.C9,Pin.OUT_PP)

    PC9.low()

    # Make a serial port object from the UART class
    BT_ser = UART(3, 115200)

    # Deconfigure default pins
    Pin(Pin.cpu.C4,  mode=Pin.ANALOG)     # Set pin modes back to default
    Pin(Pin.cpu.C5,  mode=Pin.ANALOG)

    Pin(Pin.cpu.B10,  mode=Pin.OUT_PP)     # Set pin modes back to default
    Pin(Pin.cpu.B11,  mode=Pin.OUT_PP)

    # Configure the selected pins in coordination with the alternate function table
    Pin(Pin.cpu.C10,  mode=Pin.ALT, alt=7) # Set pin modes to UART matching column 7 in alt. fcn. table
    Pin(Pin.cpu.C11, mode=Pin.ALT, alt=7)

    Pin(Pin.cpu.B13, mode=Pin.ALT, alt=4) #Set pin modes to I2C2 matching column 4 in alt. function table
    Pin(Pin.cpu.B14, mode=Pin.ALT, alt=4)

    repl_uart(BT_ser) # Change which port the repl is mirrored to