from machine import Pin, PWM
import time
import Box_Collection as bc
import Global_Variables as gv
import Button

def get_measurement_list():
    """"This function returns a list of light sensor reading"""
    
    return [gv.FL.value(), gv.L.value(), gv.R.value(), gv.FR.value()] # LOW = white HIGH = Black

def weight_measurement_list(measurement_list):
    """This function gives weights to a list of measurements equal to the sensor distances from the centre"""

    return [measurement_list[0] * -4, measurement_list[1] * -1.25, measurement_list[2] * 1.25, measurement_list[3] * 4] #update with weigtings equal to the distance of each sensor from the centre


def calc_error(weighted_measurement_list, setpoint=0):
    """This function calculates the distance from the centre then calculates the error from a setpoint"""

    temp = 0
    counter = 0 
    for value in weighted_measurement_list:
        if value != 0:
            temp += value
            counter += 1
    if counter != 0:
        measurement = temp / counter
    else:
        measurement = None
    return measurement

def calc_control_signal(error, prev_error, prev_integrator, prev_differentiator, Kp=20, Ki=0, Kd=0, tau=0.0005, T=0.05):
    """"This function calculates the control signal using a PID controller"""

    # To adjust first adjust Kp. Then adjust Ki. Then adjust Kd. If too much noise when Kd adjusted then adjust tau for more smoothing

    #calculate control signal
    proportional = Kp * error
    integrator = Ki * T/2 * (error + prev_error) + prev_integrator

    #consider differentiator on measurement rather than on error see video in notes
    differentiator = Kd * 2 * (error - prev_error)/(2*tau + T) + ((2 * tau - T)/(2 * tau + T)) * prev_differentiator
    control = proportional + integrator  + differentiator
    #print(control)
    #send control signal
    return control, integrator, differentiator

def motor_control(control_signal):
    """"This function controls motors proportionally to the control signal"""
    #print(measurement_list)
    k = 1
    speed = 50
    if control_signal < 0:
        gv.lmotor.Forward(speed + k*control_signal)
        gv.rmotor.Forward(speed - k*control_signal)

    elif control_signal > 0:
        gv.rmotor.Forward(speed - k*control_signal)
        gv.lmotor.Forward(speed + k*control_signal)
    else:
        gv.lmotor.Forward(speed)
        gv.rmotor.Forward(speed)

    #else:
    #    gv.rmotor.Forward()
    #    gv.lmotor.Forward()
    #if measurement_list == [0, 1, 1, 0] or measurement_list == [0, 0, 0, 0]:
    #    gv.rmotor.Forward(80)
    #    gv.lmotor.Forward(80)
    #    return "not at junction"
    #if measurement_list == [1, 0, 0, 0]:
    #    gv.rmotor.Forward(100)
    #    gv.lmotor.Forward(60)
    #    return "not at junction"
    #if measurement_list == [0, 1, 0, 0]:
    #    gv.rmotor.Forward(100)
    #    gv.lmotor.Forward(40)
    #    return "not at junction"
    #if measurement_list == [0, 0, 1, 0]:
   #     gv.rmotor.Forward(40)
    #    gv.lmotor.Forward(100)
     #   return "not at junction"
    #if measurement_list == [0, 0, 0, 1]:
     #   gv.rmotor.Forward(60)
       # gv.lmotor.Forward(100)
      #  return "not at junction"
    #if measurement_list == [0, 0, 1, 1] or measurement_list == [1, 1, 1, 1]:
     #   gv.rmotor.off()
      #  gv.lmotor.off()
        #print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
       # return "at junction"
    #if measurement_list == [1, 1, 0, 0] or measurement_list == [1, 1, 1, 1]:
     #   gv.rmotor.off()
      #  gv.lmotor.off()
        #print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
       # return "at junction"

def detect_L_turn(measurement_list):
    """"This function detects if there is a left turn"""

    detection_list = [1*measurement_list[0], 1*measurement_list[1], 0*measurement_list[2], 0*measurement_list[3]]
    if detection_list == [1, 1, 0, 0]:
        return "at junction"

def detect_R_turn(measurement_list):
    """"This function detects if there is a right turn"""

    detection_list = [0*measurement_list[0], 0*measurement_list[1], 1*measurement_list[2], 1*measurement_list[3]]
    if detection_list == [0, 0, 1, 1]:
        return "at junction"

#def detect_dropoff(measurement_list):
#    """"This function detects if there is no line"""
#
#    if measurement_list == [0, 0, 0, 0]:
#        return "at junction"

#def detect_T_junction(measurement_list):             ### I believe this function is redundant due to detect_R_turn & detect_L_Turn
#    """"This function detects if there is a T junction"""
#
#    if measurement_list == [1, 1, 1, 1]:
#        return "at junction"

def junc_detection(measurement_list):
    if detect_R_turn(measurement_list) == "at junction" or detect_L_turn(measurement_list) == "at junction":
        gv.junc_counter += 1
        if gv.junc_counter > 5:
            return "at junction"
    else:
        return "not at junction"

def line_following(pickup = False, dropoff = False, blind=False, blind_time=0):
    """This function follows a line until a junction is detected"""
    
    gv.junc_counter = 0
    state = "not at junction"   
    prev_error = 0
    prev_integrator = 0
    prev_differentiator = 0
    control_signal = 0
    #qr_code_detected = False
    
    time_remaining = blind_time
    
    counter = 0
    
    while state == "not at junction":
        start_time = time.time_ns()
        measurement_list = get_measurement_list()
        counter += 1
        #print(measurement_list)
        #print(counter)
        weighted_measurement_list = weight_measurement_list(measurement_list)
        error = calc_error(weighted_measurement_list)
        if error == None:
            error = prev_error
        results = calc_control_signal(error, prev_error, prev_integrator, prev_differentiator)

        control_signal = results[0]
        prev_error = error
        prev_integrator = results[1]
        prev_differentiator = results[2]
        
        state = junc_detection(measurement_list)

        Button.button_interupt()
        
        motor_control(control_signal)

        time.sleep(0.05)

        end_time = time.time_ns()
        
        #print(control_signal)

        #detect_R_turn(measurement_list)
        #detect_L_turn(measurement_list) # Do not need a detect T junction
        #print(state)
        #if dropoff == True:
         #   detect_dropoff(measurement_list)   
        
        if blind == True:
            time_elapsed = end_time - start_time
            time_remaining = time_remaining - time_elapsed
            if time_remaining < 0:
                state = "blind finished"

        if pickup == True:
            bc.detect_box()
        if pickup == False:
            gv.box_status = bc.box_still_on()
        
    gv.rmotor.off()
    gv.lmotor.off()
        
            
        #    if qr_code_detected == False:
        #        qr_code = bc.get_qr_code()
        #        if qr_code is not None:
        #            qr_code_detected = True
    
    #if pickup == True and qr_code_detected == True:
     #   return qr_code

def turn_clockwise(speed):
    """"This function turns the robot 90 degrees clockwise"""

    gv.rmotor.off()
    gv.lmotor.off()
    gv.rmotor.Reverse(speed)
    gv.lmotor.Forward(speed)
    if speed == 100:
        time.sleep(0.57)
    elif speed == 70:
        time.sleep(1.2)
    gv.rmotor.off()
    gv.lmotor.off()

def turn_anticlockwise(speed):
    """"This function turns the robot 90 degrees anticlockwise"""

    gv.rmotor.off()
    gv.lmotor.off()
    gv.rmotor.Forward(speed)
    gv.lmotor.Reverse(speed)
    if speed == 100:
        time.sleep(0.57)
    elif speed == 70:
        time.sleep(1.2)
    gv.rmotor.off()
    gv.lmotor.off()

def blind_forward(distance_wanted):
    """This function makes the robot move forwards a certain distance without taking into account the light sensors"""
    gv.rmotor.Forward(100)
    gv.lmotor.Forward(100)
    time.sleep(distance_wanted) #1cm goes to 18cm
    gv.rmotor.off()
    gv.lmotor.off()

def blind_reverse(distance_wanted):
    """This function makes the robot move forwards a certain distance without taking into account the light sensors"""
    gv.rmotor.Reverse(100)
    gv.lmotor.Reverse(100)
    time.sleep(distance_wanted) # 1s goes to 18cm
    gv.rmotor.off()
    gv.lmotor.off()

def slow_to_stop():
    """This function makes the robot slow from a speed of 50 to 0"""
    speed = 50
    for i in range(50):
        gv.rmotor.Forward(speed-1)
        gv.lmotor.Forward(speed-1)
        time.sleep(0.001)