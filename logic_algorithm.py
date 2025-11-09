# importing required functions from other files in the same directory
import Box_Collection
import Line_Following
import Button
import Global_Variables as gv


#importing libraries used in this file
import time


# defining constants for distance of blind movements 
# each constant defines a tunable distance the robot needs to move at each key locations on the board
SMALL = 8/20
CLOCK_SMALL = 4/20
TEMP_BLIND = 9/20
OUT_OF_HOME = 20/20
OUT_OF_BAY = 10/20
STEP_FWD = 40
TINY_QR_FWD = 1/20
OUT_OF_COLORED_BAYS = 10/20
FWD_HOME = 20/20


# the dictionary connections defines the graph of key nodes on the graph to be used for navigation
# this dictionary also contains the relative direction of one node from another
connections = {
    "Home": {"Yellow": 270, "Green": 90},
    "Yellow": {"Red": 270, "Home": 90},
    "Green": {"Home": 270, "Blue": 90},
    "Red": {"L_purple": 180, "Yellow": 90},
    "Blue": {"L_orange": 180, "Green": 270},
    "L_orange": {"Blue": 0, "J_L_orange": 180},
    "L_purple": {"Red": 0, "J_L_purple": 180},
    "J_L_orange": {"L_orange": 0, "Ramp": 270},
    "J_L_purple": {"L_purple": 0, "Ramp": 90},
    "Ramp": {"U_T": 0, "J_L_orange": 90, "J_L_purple": 270},
    "U_T": {"J_U_orange": 90, "Ramp": 180, "J_U_purple": 270},
    "J_U_orange": {"U_orange": 180, "U_T": 270},
    "J_U_purple": {"U_purple": 180, "U_T": 90},
    "U_orange": {"J_U_orange": 0},
    "U_purple": {"J_U_purple": 0}
    }


# path_det is a secondary dictionary to show the relative locations of each node, showing which node is closest to which node.
# this dictionary will be used for the function mini_pathfinding
path_det = {
    "Home": 5,
    "Yellow": 6,
    "Green": 4,
    "Red": 7,
    "Blue": 3,
    "L_purple": 8,
    "L_orange": 2,
    "Ramp": None
}


#the class State is used to define the state of the robot
class State:
    """
    global class containing all information about the state of the robot
    self.loc: location of the robot
    self.orien: orientation of the robot, with 0 degrees meaning the robot points towards the side of the map with the four colored loading/unloading bays
    self.destination: destination of the robot at the moment, which of the four shelf the robot will be depositing the box it is carrying
    self.bay: which exact bay, out of six, does the box belong to within each row of shelves
    self.remaining_boxes: contains the bays which still have not yet been unloaded in phase 1
    self.phase tells the robot which phase it is in (phase 1 is when all 4 bays have boxes, phase 2 is when only a box is added one by one)
    self.q is a temporary state variable used for error handling if the reset button is pressed during the operation of the robot. It is only used if the button is pressed during operation
    """

    def __init__(self, loc, orien):
        self.loc = loc
        self.orien = orien
        self.destination = None
        self.bay = None
        self.remaining_boxes = ["Red", "Blue", "Green", "Yellow"]
        self.phase = 1
        self.q = 0
        

# the global variable state is initialized
global state
state = State("Home", 180)

# Defining the functions required for the operation of the robot

def crashed(phase):
    """
    function to reset the state of the robot to inital state in the case that the button is pressed during the operation of the robot
    """
    state.loc = "Home"
    state.orien = 180
    state.phase = phase
    state.q = 0


def mini_path_find(start, dest, min_max):
    """
    pathfinds a route from loading/unloading bay to a desired lower shelf or the ramp by finding the shortest path.
    The shortest path is determined by the starting position, and from this the robot decides to go clockwise or anticlockwise
    A list of nodes the robot has to pass to reach the destination the msot efficiently is returned
    """

    queue = [start]
    while start != dest:
        branches = list(connections[start].keys())
        if min_max == "min":
            start = min(branches, key = lambda branches: path_det[branches])
        elif min_max == "max":
            start = max(branches, key = lambda branches: path_det[branches])
            
        queue.append(start)
    print(queue)
    return queue

def path_find(start, dest):
    """
    the complete path from current location to destination is returned
    pathfinds from a loading/unloading bay to the desired shelf, even if the shelf is on the upper level
    outputs an array with all the nodes to pass
    """

    if dest == "L_orange":
        return mini_path_find(start, dest, "min")
    elif dest == "L_purple":
        return mini_path_find(start, dest, "max")
    elif dest == "U_purple" or dest == "U_orange":
        if start == "Red" or start == "Yellow":
            queue = mini_path_find(start, "L_purple", "max")
            queue.append("J_L_purple")
        elif start == "Green" or start == "Blue":
            queue = mini_path_find(start, "L_orange", "min")
            queue.append("J_L_orange")
        else:
            raise Exception("error 2, elifs ran out")
        queue.append("Ramp")
        queue.append("U_T")
        queue.append("J_" + dest)
        queue.append(dest)
        return queue
        
    else:
        raise Exception("error 1, elifs ran out")
    



def fwd_until_junc():
    """
    function that makes the robot move forward until a junction is detected
    """
    Line_Following.line_following(pickup=False)

def clockwise(complete=False, speed = 100):
    """
    function that makes the robot turn clockwise then slightly move forwards past the junction
    The slight forward movement action can be skipped if complete == True is passed to it. This is used when making the robot turn 180 degrees instead of just 90 degrees
    """
    Line_Following.turn_clockwise(speed)
    if complete == False:
        Line_Following.blind_forward(CLOCK_SMALL)

def anticlockwise(complete=False, speed = 100):
    """
    function that makes the robot turn anticlockwise then slightly move forwards past the junction
    The slight forward movement action can be skipped if complete == True is passed to it. This is used when making the robot turn 180 degrees instead of just 90 degrees
    """
    Line_Following.turn_anticlockwise(speed)
    if complete == False:
        Line_Following.blind_forward(CLOCK_SMALL)

def load_fork():
    """
    This function lifts the fork from the ground up to the travelling height
    """
    Box_Collection.lift_block()

def unload_fork():
    """
    This function lowers the fork from the travelling height to the bay height, taking into account the different bay height in the upper and lower racks
    """
    if state.destination == "U_orange" or state.destination == "U_purple":
        Box_Collection.lower_to_ground()
    elif state.destination == "L_orange" or state.destination == "L_purple":
        Box_Collection.lower_onto_rack()

def fwd_until_black():
    """
    This function makes the robot line follow for 2 seconds, the distance for the robot to reach the loading or unloading racks
    """
    Line_Following.line_following(blind = True, blind_time = 2 * 1000000000)

def fwd_until_box():
    """
    This function makes the robot line follow until the robot reaches the box
    """
    Line_Following.line_following(pickup=True)

def fwd(distance):
    """
    This function makes the robot move forward without line following for a specified distance
    """
    Line_Following.blind_forward(distance_wanted = distance)

def is_RHS_lidar_pos():
    """
    placeholder function for the implementation of right lidar sensor for phase 2 detection of boxes
    """
    pass

def is_LHS_lidar_pos():
    """
    placeholder function for the implementation of left lidar sensor for phase 2 detection of boxes
    """
    pass

def rvs(distance):
    """
    This function makes the robot move in reverse without line following for a specified distance
    """
    Line_Following.blind_reverse(distance_wanted = distance)

def parse_qr(text):
    """
    This function parses the qr code read by the qr code sensor and outputs a destination and bay position
    """
    translator = {
        "A": "orange",
        "B": "purple",
        "upper": "U",
        "lower": "L"
    }

    parts = [part.strip() for part in text.split(',')]

    # Extract the parts we are interested in
    rack = parts[0].split()[1]
    level = parts[1]
    position = parts[2]

    destination = translator[level.lower()] + "_" + translator[rack.upper()]
    return destination, int(position)

def count_unload_return():
    """
    counts how many bays it has moved past and turns into the desired bay.
    tells robot to unload and return back to original position
    """
    print(state.bay)
    counter = 0
    if state.destination == "U_purple" or state.destination == "L_orange":
        dest_general = 7 - state.bay
    else:
        dest_general = state.bay
    print(dest_general)
    while counter < dest_general:
        fwd_until_junc()
        fwd(SMALL)
        print(counter)
        counter += 1
    turn_unload_return(dest_general)

def execute_travel(route):
    """
    Tells the robot to move according to the list of nodes provided.
    Contains code to ignore loading bay lines on the bottom floor if the target destination is on the top floor
    """
    destination = route[-1]
    output = route.copy()
    next_node = route.pop(0)
    while route:
        current_node = next_node
        next_node = route.pop(0)
        print(current_node, next_node)
        wanted_orien = connections[current_node][next_node]
        #clockwise is positive
        turn_angle = wanted_orien - state.orien
        if turn_angle == 90 or turn_angle == -270:
            clockwise()
            state.orien = (state.orien + 90) % 360
        elif turn_angle == -90 or turn_angle == 270:
            anticlockwise()
            state.orien = (state.orien - 90) % 360
        elif turn_angle == 180 or turn_angle == -180:
            clockwise(complete = True)
            clockwise()
            state.orien = (state.orien + 180) % 360
        elif turn_angle == 0 or turn_angle == 360 or turn_angle == -360:
            fwd(SMALL)
        if {current_node, next_node} in [{"Blue", "L_orange"}, {"Red", "L_purple"}] and not state.destination in ["L_purple", "L_orange"]:
            for i in range(7):
                fwd_until_junc()
                fwd(SMALL)
        fwd_until_junc()
        state.loc = next_node
        print(turn_angle)
    # print("\n\n\n\n")
    return output

def return_to_color(path_fwd):
    """
    instructs the robot to move back to the colored loading/unloading bays from its current location at the racks
    """
    path_rvs = path_fwd[::-1]
    while path_rvs[-2] in ["Red", "Yellow", "Green", "Blue"]:
        print(path_rvs)
        path_rvs.pop()
    execute_travel(path_rvs)


def phase_1_find_box():
    """
    starting at either Red or Blue pointing to 0 degrees, make the robot go to the nearest bay with a box and turn to face the box
    """
    color_order = ["Red", "Yellow", "Green", "Blue"]
    if state.loc == "Red":
        i = 0
        while not state.loc in state.remaining_boxes:
            if i == 0:
                clockwise()
            fwd_until_junc()
            color_order.pop(0)
            state.loc = color_order[0]
            i += 1
        if i != 0:
            anticlockwise()

    elif state.loc == "Blue":
        color_order = color_order[::-1]
        i = 0
        while not state.loc in state.remaining_boxes:
            if i == 0:
                anticlockwise()
            fwd_until_junc()
            color_order.pop(0)
            state.loc = color_order[0]
            i += 1
        if i != 0:
            clockwise()
    else:
        raise Exception("error sth, elifs ran out")
    
def GO_HOME():
    """
    Function to make the robot go back home, given the robot position is the Red or Blue junction
    """
    if state.loc == "Red":
        i = 0
        clockwise()
        while i<2:
            fwd_until_junc()
            fwd(SMALL)
            i += 1
        anticlockwise()
        fwd_until_junc()
        fwd(FWD_HOME)

    elif state.loc == "Blue":
        i = 0
        anticlockwise()
        while i<2:
            fwd_until_junc()
            fwd(SMALL)
            i += 1
        clockwise()
        fwd_until_junc()
        fwd(FWD_HOME)
    else:
        raise Exception("error sth, elifs ran out")

def go_in_for_the_box_readqr():
    """
    with the bot facing the box, go straight in for the box, scan the qr code, lift the box, and move back to initial position
    """
    fwd(SMALL)
    text = None
    counter = 0
    while text == None and counter < 50:
        counter += 1
        text = Box_Collection.get_qr_code()
        Line_Following.line_following(blind = True, blind_time = 0.2 * 1000000000)
    Line_Following.line_following()
    destination, bay = parse_qr(text)
    Line_Following.blind_forward(TEMP_BLIND)
    load_fork()
    time.sleep(0.3)
    rvs(OUT_OF_COLORED_BAYS)
    if state.loc == "Red" or state.loc == "Yellow":
        clockwise(complete = True, speed = 70)
        clockwise(speed = 70)
    elif state.loc == "Blue" or state.loc == "Green":
        anticlockwise(complete = True, speed = 70)
        anticlockwise(speed = 70)
    
    fwd_until_junc()
    state.orien = 180
    state.remaining_boxes.remove(state.loc)
    return destination, bay

def phase_2_detect_boxes():
    """
    moves from bay to bay, using the lidar sensor to detect whether a box is present in that bay
    """

    color_order = ["Red", "Yellow", "Green", "Blue"]
    if state.loc == "Red":
        clockwise()
        while not is_LHS_lidar_pos():
            color_order.pop(0)
            if not color_order:
                print("NO BOXES DETECTED")
                anticlockwise()
                phase_2_detect_boxes()
            fwd_until_junc()
            state.loc = color_order[0]
        anticlockwise()

    elif state.loc == "Blue":
        color_order = color_order[::-1]
        anticlockwise()
        while not is_RHS_lidar_pos():
            color_order.pop(0)
            if not color_order:
                print("NO BOXES DETECTED")
                anticlockwise()
                phase_2_detect_boxes()
            fwd_until_junc()
            state.loc = color_order[0]
        clockwise()
    else:
        raise Exception("error sth, elifs ran out")


def turn_unload_return(bay):
    """
    Instructs the robot to turn, move towards the rack, unload and return to the initial position
    """
    
    if state.destination == "U_purple" or state.destination == "L_orange":
        clockwise()
    elif state.destination == "L_purple" or state.destination == "U_orange":
        anticlockwise()
    else:
        raise Exception("error 3, elifs ran out")
    fwd_until_black()
    unload_fork()

    rvs(OUT_OF_BAY)
    clockwise(complete = True)
    clockwise()
    fwd_until_junc()
    if state.destination == "U_purple" or state.destination == "L_orange":
        anticlockwise()
    elif state.destination == "L_purple" or state.destination == "U_orange":
        clockwise()
    else:
        raise Exception("error 3, elifs ran out")
    state.orien = 0
    if bay != 1:
        for i in range(bay-1):
            fwd_until_junc()
    fwd(SMALL)
    #this is a very fragile part of the code, the bot has to turn quite accurately

def start_at_yellow():
    """
    Instructs the robot to move from home to the first loading bay with a box.
    """
    if "Yellow" in state.remaining_boxes():
        fwd_until_junc()
        gv.led_enable.value(1)
        fwd(SMALL)
        fwd_until_junc()
        clockwise()
        fwd_until_junc()
        clockwise()
        state.loc = "Yellow"
        state.orien = 0
    elif "Red" in state.remaining_boxes():
        fwd_until_junc()
        gv.led_enable.value(1)
        fwd(SMALL)
        fwd_until_junc()
        clockwise()
        fwd_until_junc()
        fwd(SMALL)
        fwd_until_junc()
        clockwise()
        state.loc = "Red"
        state.orien = 0
    elif "Green" in state.remaining_boxes():
        fwd_until_junc()
        gv.led_enable.value(1)
        fwd(SMALL)
        fwd_until_junc()
        anticlockwise()
        fwd_until_junc()
        anticlockwise()
        state.loc = "Green"
        state.orien = 0
    elif "Blue" in state.remaining_boxes():
        fwd_until_junc()
        gv.led_enable.value(1)
        fwd(SMALL)
        fwd_until_junc()
        anticlockwise()
        fwd_until_junc()
        fwd(SMALL)
        fwd_until_junc()
        anticlockwise()
        state.loc = "Blue"
        state.orien = 0


def main():
    """
    Runs the entire program, telling the robot to do phase 1 (boxes in all 4 bays)
    Instructs the robot to move the box into the racks bay by bay until all 4 racks are completed, then instructs the robot to return to home
    We also introduce error handing in the case that the button is pressed during the operation of the robot
    """
    while True:
        HOMIE = 1
        gv.rmotor.off()
        gv.lmotor.off()
        state.q = 0
        Button.button_to_start()
        
        Box_Collection.initialise_servo()
        while not state.remaining_boxes.empty():
            if state.q == 0:
                start_at_yellow()
                state.q = 1
            else:
                phase_1_find_box()
            try:
                state.destination, state.bay = go_in_for_the_box_readqr()
            except:
                crashed()
                HOMIE = 0
                break
            route = path_find(state.loc, state.destination)
            try:
                route = execute_travel(route)
                count_unload_return()
                return_to_color(route)
            except:
                crashed()
                HOMIE = 0
                break
        if HOMIE == 1:
            GO_HOME()
            return 0
    
    # commented out the phase 2 code as lidar implentation was not completed
    # for p in range(90):
    #     try:
    #         phase_2_detect_boxes()
    #     except:
    #         crashed()
    #         break
    #     try:
    #         state.destination, state.bay = go_in_for_the_box_readqr()
    #     except:
    #         crashed()
    #         break
    #     try:
    #         route = path_find(state.loc, state.destination)
    #         route = execute_travel(route)
    #         count_unload_return()
    #         return_to_color(route)
    #     except:
    #         crashed()
    #         break
