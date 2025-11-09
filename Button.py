import Global_Variables as gv
import time

def button_to_start():
    """
    This function waits until the button is pressed until it is passed
    """

    while gv.Button.value() != 1:
        time.sleep(1)
    print("START!")

def button_interrupt():
    """
    This function raises an exception if the button is pressed
    """

    if gv.Button.value() == 1:
        raise Exception("Button Pressed")
