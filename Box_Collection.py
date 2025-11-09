from machine import Pin, PWM, SoftI2C, I2C
from utime import sleep
import Global_Variables as gv
from libs.tiny_code_reader.tiny_code_reader import TinyCodeReader
from libs.DFRobot_TMF8x01.DFRobot_TMF8x01 import DFRobot_TMF8801, DFRobot_TMF8701

def change_height(target_level):
    """
    This function changes the servo to a target level
    """

    servo_PWM = PWM(Pin(15), 100)
    u16_level = int(65535 * target_level / 100)
    servo_PWM.duty_u16(u16_level)

def initialise_servo():
    """
    This function sets the servo to the lowest desired level
    """

    change_height(6.2)

def lower_to_ground():
    """
    This function sets the servo to a level where robot fork is low enough to put a box on a level floor
    """

    change_height(6.2)

def lower_onto_rack():
    """
    This function sets the servo to a level where the robot fork could put a box on the rack
    """


    change_height(12)

def lift_block():
    """
    This function sets the servo to a level where a box would be lifted off the floor
    """

    change_height(14.5)
    
def travel_position():
    """
    This function sets the servo to a level where the robot fork is at a safe height to travel at
    """


    change_height(10)

def get_f_distance():
    """
    This function returns the forward distance
    """

    while True:
        if(gv.tmf8701.is_data_ready() == True):
            return gv.tmf8701.get_distance_mm()
        counter += 1
        sleep(0.05)
        if counter > 5:
            print("Box not found")
            break

def detect_box(d = 2):
    """
    This function detects when within d mm of a box
    """

    if get_f_distance() < d:
        return "Box collected"
    else:
        return "not at junction"

def get_qr_code():
    """
    This function tries to scan a qr code
    """

    gv.qr_enable.value(1)
    sleep(TinyCodeReader.TINY_CODE_READER_DELAY)
    sleep(0.1) #WE CAN SPEED THIS UP A BIT EXPERIMENTALLY
    code = gv.tiny_code_reader.poll()
    counter = 0
    while code == None and counter <= 10:
        sleep(TinyCodeReader.TINY_CODE_READER_DELAY)
        code = gv.tiny_code_reader.poll()
        counter += 1
    print(code)
    gv.qr_enable.value(0)
    return code


# The below function was never implemented
# The purpose was so that if the robot dropped a box in transit the robot would not continue on to a bay and would instead go back to get a new box
#def box_still_on():
#    """
#    This function detects if the box is still on the fork
#    """

#    TOF = get_f_distance()
#    LENGTH_OF_FORK = 10
#    if TOF > LENGTH_OF_FORK:
#        return "No Box"
#    else:
#        return "Yes Box"