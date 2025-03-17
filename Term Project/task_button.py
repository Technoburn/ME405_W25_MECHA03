from button import ButtonArray
from task_share import Share

class Task_Button:
    def __init__(self, bump:Share, buttons:ButtonArray):
        '''
        The `Task_Button` task continuously monitors the `ButtonArray` object 
        and reads the state of all bump sensors, and updates a shared 
        `bump`, based on if any single bump sensor was pressed or not.   

        :param bump: A `Share` that reads `False` if just one bump sensor 
            in the array was pressed, `True` otherwise      
        :param buttons: `ButtonArray` object of all bump sensors.
        '''    
        
        # Copy parameters to properties
        self.bump = bump
        self.buttons = buttons

        # States of the FSM
        self.S0_RUN = 0

        # Preinitialization
        # This code before the loop initializes the Python code and structure of
        # FSM but does not initialize the FSM itself
        self.state = self.S0_RUN

    def task(self):
        '''Generator Function to run implemented Finite-State Machine'''

        while True:
            if self.state == self.S0_RUN:
                self.bump.put(self.buttons.read_all())

            yield self.state