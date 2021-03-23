from pylgbst import *
from pylgbst.hub import MoveHub
from robot import *
from time import sleep
from csv import reader
import six

BTN_FORWARD=19
BTN_BACKWARD=26
BTN_LEFT=13

logging.basicConfig(level = logging.WARN)
log = logging.getLogger("test")

mac="00:16:53:B2:30:37"
conn = get_connection_bluegiga(hub_mac=mac)

print("Connected.")

robot = Robot(conn)
robot.addButton(BTN_BACKWARD)
robot.addButton(BTN_FORWARD)
robot.addButton(BTN_LEFT)

#################################################################

UP = 1
DOWN = -1
running = True
processing = False

STEP_X=20
STEP_Y=15
STEP_Z=25 #PEN
SPEED_X=SPEED_Y=0.3
SPEED_Z=0.5

CURR_X = CURR_Y = 0
CURR_CMD = 0
lastFile='plot2.csv'

def motorCallback(pos):
    print(pos)

def readCommands(filename):
    with open(filename, 'r') as read_obj:
        csv_reader = reader(read_obj, delimiter=';')
        ret = []
        for row in csv_reader:
            # row variable is a list that represents a row in csv
            print(row)
            ret.append(row)
        return ret
    return []

def cmdPenUp(robot):
    global STEP_Z
    print("* Pen up")
    robot.motor_external.angled(STEP_Z, SPEED_Z)

def cmdPenDown(robot):
    global STEP_Z
    print("* Pen down")
    robot.motor_external.angled(STEP_Z, -SPEED_Z)

def cmdMove(robot, x, y):
    global STEP_X, STEP_Y, CURR_X, CURR_Y
    print("* Move +%s,+%s" % (x, y) )
    if x != 0:
        robot.motor_B.angled(x * STEP_X, SPEED_X)
    if y != 0:
        robot.motor_A.angled(y * STEP_Y, SPEED_Y)
    CURR_X=CURR_X+x
    CURR_Y=CURR_Y+y

def cmdAbs(robot, x, y):
    global CURR_X, CURR_Y, STEP_X, STEP_Y
    print("* Move to %s,%s" % (x, y) )
    diff_x=CURR_X - x
    diff_y=CURR_Y - y
    if diff_x != 0:
        robot.motor_B.angled(diff_x * STEP_X, SPEED_X)
    if diff_y != 0:
        robot.motor_A.angled(diff_y * STEP_Y, SPEED_Y)
    CURR_X=x
    CURR_Y=y

def processCommand(robot, cmd):
    if len(cmd)>0:
        if cmd[0] == "PEN" and cmd[1] == "UP":
            cmdPenUp(robot)

        if cmd[0] == "PEN" and cmd[1] == "DOWN":
            cmdPenDown(robot)

        if cmd[0] == "PEN" and cmd[1] == "POINT":
            cmdPenDown(robot)
            cmdPenUp(robot)

        if cmd[0] == "ABS" and len(cmd)>2: #absolute position
            x=int(cmd[1])
            y=int(cmd[2])
            cmdAbs(robot, x, y)
        if cmd[0] == "MOVE" and len(cmd)>2: #relative position
            x=int(cmd[1])
            y=int(cmd[2])
            cmdMove(robot, x, y)

        if cmd[0] == "ZERO":
            global CURR_X, CURR_Y
            CURR_X=0
            CURR_Y=0

robot.setMotorCallback(motorCallback)

print("please move PEN down")
inp = six.moves.input("[Enter]")
print("Trank you")

cmdPenUp(robot)

try:
    while True:
        print("===========================================")
        print("         Welcome :)")
        print("===========================================")
        print("Interactive [i] or load commands from file?")
        inp = six.moves.input("i/q/filename? ")

        if inp == "i" or inp == "I":
            processing = True
            while processing:
                inp = six.moves.input("> ")
                cmd = inp.split(" ")
                processCommand(robot, cmd)
                if inp == "q":
                    break
            break

        if inp == "q":
            break

        if inp == "":
            inp = lastFile
        else:
            lastFile = inp

        print("Reading commands from file...")
        commands = readCommands(inp)
        print(" %i commands read" % len(commands))
        print("press start button to start")
        CURR_CMD=0

    
        while running and CURR_CMD < len(commands):

            if robot.isButtonPressed(BTN_BACKWARD):
                processing = not(processing)
                if processing:
                    print("Starting...")
                else:
                    print("Paused.")

            if processing:
                cmd = commands[CURR_CMD]
                print("cmd: %s" % cmd)
                processCommand(robot, cmd)
                CURR_CMD=CURR_CMD+1

            sleep(0.1)

        print("Done")
        cmdAbs(robot, 0 ,0) #return home

finally:
    print("Goodbye")
    GPIO.cleanup()

