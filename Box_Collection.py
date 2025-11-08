from machine import Pin, PWM, SoftI2C, I2C
from utime import sleep
import Global_Variables as gv
from libs.tiny_code_reader.tiny_code_reader import TinyCodeReader
from libs.DFRobot_TMF8x01.DFRobot_TMF8x01 import DFRobot_TMF8801, DFRobot_TMF8701

"""def get_servo_angle():
   """"""reads the analogue feedback of the servo to get the current angle""""""
   angle=gv.adc.read_u16()*0.47-33.4 #this is the function on the servo documentation to get the angle from the analogue output
   return angle"""

def change_height(target_level):
    servo_PWM = PWM(Pin(15), 100)
    u16_level = int(65535 * target_level / 100)
    servo_PWM.duty_u16(u16_level)

    #if target_level > current_level:
    #    direction = 1
    #if target_level < current_level:
    #    direction = -1
    #while current_level != target_level:
        
    #    u16_level = int(65535 * current_level / 100)
    #    servo_PWM.duty_u16(u16_level)
    
        #update level and sleep
    #    print(f"Level={current_level}, u16_level={u16_level}, direction={direction}")
    #    current_level += direction
    #    sleep(0.1)

def initialise_servo():
    change_height(6.2)

def lower_to_ground():
    change_height(6.2)

def lower_onto_rack():
    change_height(12)

def lift_block():
    change_height(14.5)
    
def travel_position():
    change_height(10)

# def initalise_servo():
#     """This function initialises the servo motor"""
#     gv.level = 0 #or a different level if this is too low for the forks to insert into the pallet
     
#     #select pin
#     pwm_pin_no = 28  # Pin 28 = GP28 (labelled 34 on the jumper), replace with correct pin
#     gv.servo_pin = PWM(Pin(pwm_pin_no), 100)

#     #level-to-height ratio is 0.8836

#     #the initial level should be added to the other levels if it is not zero
#     u16_level = int(65535 * gv.level / 100)
#     gv.servo_pin.duty_u16(u16_level)

# def lift_block():
#     """lifts block 20mm off the ground"""
#     while gv.level<23: #or 34, if the block can be raised to 30mm right away
#         direction=1
#         gv.level += direction
#         u16_level = int(65535 * gv.level / 100)
#         gv.servo_pin.duty_u16(u16_level)
   
# def raise_to_rack(): #this is not needed if the block can be raised to 30mm right away
#     """raises block to the height of the unloading rack"""
#     while gv.level<34:
#         direction=1
#         gv.level += direction
#         u16_level = int(65535 * gv.level / 100)
#         gv.servo_pin.duty_u16(u16_level)

# def lower_onto_rack():
#     """lowers block onto rack"""
#     while gv.level>28:
#         direction=-1
#         gv.level += direction
#         u16_level = int(65535 * gv.level / 100)
#         gv.servo_pin.duty_u16(u16_level)

# def lower_to_ground():
#     """lowers forks back to 0 displacement after a block has been placed"""
#     while gv.level>0:
#         direction=-1
#         gv.level += direction
#         u16_level = int(65535 * gv.level / 100)
#         gv.servo_pin.duty_u16(u16_level)

def get_f_distance():
    """This function returns the forward distance"""
    while True:
        if(gv.tmf8701.is_data_ready() == True):
            return gv.tmf8701.get_distance_mm()
        counter += 1
        sleep(0.05)
        if counter > 5:
            print("Box not found")
            break

def detect_box():
    """This function detects when within d mm of a box"""
    d = 2
    if get_f_distance() < d:
        return "Box collected"
    else:
        return "not at junction"
    
def box_still_on():
    """This function detects if the box is still on the fork"""
    TOF = get_f_distance()
    LENGTH_OF_FORK = 10
    if TOF > LENGTH_OF_FORK:
        return "No Box"
    else:
        return "Yes Box"

def get_qr_code():
    """This function gets a qr code"""
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

#def get_s_distance():
    """This function returns the side distance using TMF8801"""
#    counter = 0

#    i2c_bus = I2C(id=0, sda=Pin(8), scl=Pin(9), freq=100000)
#    tof = DFRobot_TMF8801(i2c_bus=i2c_bus)
#    while(tof.begin() != 0):
#      counter += 1
#      if counter > 100:
#          break
#      sleep(0.5)
#    tof.start_measurement(calib_m = tof.eMODE_NO_CALIB)
  
#   while True:
#     if(tof.is_data_ready() == True):
#       return tof.get_distance_mm()
#     counter += 1
#      if counter > 100:
#        break
#    return tof.get_distance_mm()

#def findbox():

