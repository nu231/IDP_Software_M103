import Global_Variables as gv
import time

def button_to_start():
    while gv.Button.value() != 1:
        time.sleep(1)
    print("START!")

def button_interrupt():
    if gv.Button.value() == 1:
        raise Exception("Button Pressed")
