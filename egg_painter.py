from pylgbst import *
from pylgbst.hub import MoveHub
from robot import *
from time import sleep
from csv import reader
from os import path
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

global STEP_X, STEP_Y, STEP_Z, SPEED_X, SPEED_Y, CURR_X, CURR_Y, CURR_Z
STEP_X=-15 #-15 => 360° = 225
STEP_ROUND=225
STEP_Y=8 # 8 => -55 - 
STEP_Z=180 #PEN
SPEED_X=0.3
SPEED_Y=0.1
SPEED_Z=0.3

CURR_X = 0
CURR_Y = 0
CURR_Z = 0
CURR_CMD = 0
lastFile='plot2.csv'
sensorMovement=False

def sensorCallback(color, distance):
    global sensorMovement
    print("color=%d b=%f" % (color,distance))
    sensorMovement=True

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
    global STEP_Z, CURR_Y, SPEED_Z
    print("* Pen up")
    #CURR_Z=CURR_Z+STEP_Z
    robot.motor_external.angled(STEP_Z, SPEED_Z)

def cmdPenDown(robot):
    global STEP_Z, CURR_Z, SPEED_Z
    print("* Pen down")
    CURR_Z=CURR_Z-STEP_Z
    robot.motor_external.angled(STEP_Z, -SPEED_Z)

def cmdPenMove(robot, z):
    global STEP_Z, CURR_Z, SPEED_Z
    print("* Pen Move: %d" % z)
    CURR_Z=CURR_Z-STEP_Z
    robot.motor_external.angled(z, -SPEED_Z)

def cmdMove(robot, x, y):
    global STEP_X, STEP_Y, CURR_X, CURR_Y, SPEED_X, SPEED_Y
    print("* Move +%s,+%s" % (x, y) )
    if x != 0 and y != 0:
        print("2x MOVE")
        t=x*STEP_X
        t2=y*STEP_Y
        fac=x/y
        sx=SPEED_X #SPEED_X == 1
        sy=SPEED_Y*fac #SPEED Y == fac
        if x<y:
            t=y*STEP_Y
            t2=x*STEP_X
            fac=y/x
            sx=SPEED_X * fac
            sy=SPEED_Y
        print("motor_AB(%f, %f, %f) fac=%f" % (t, sx, sy, fac))
        robot.motor_AB.timed(SPEED_X, -sx, sy)
    elif x != 0:
        robot.motor_A.angled(x * STEP_X, SPEED_X)
    elif y != 0:
        robot.motor_B.angled(y * STEP_Y, SPEED_Y)
    CURR_X=CURR_X+x
    CURR_Y=CURR_Y+y

def cmdAbs(robot, x, y):
    global CURR_X, CURR_Y, STEP_X, STEP_Y
    print("* Move to %s,%s" % (x, y) )
    diff_x=- CURR_X - x
    diff_y=- CURR_Y - y
    print(" diff: %i,%i" % (diff_x, diff_y))
    if diff_x != 0:
        robot.motor_A.angled(diff_x * STEP_X, SPEED_X)
    if diff_y != 0:
        robot.motor_B.angled(diff_y * STEP_Y, SPEED_Y)
    CURR_X=x
    CURR_Y=y

def cmdMoveStart(robot):
    global CURR_X, CURR_Y, STEP_Y, SPEED_Y, sensorMovement
    robot.motor_B.angled(10*STEP_Y, SPEED_Y)
    sensorMovement=False
    print("Moving Y until in sensor range")
    while not sensorMovement:
        robot.motor_B.start_speed(-SPEED_Y)

    robot.motor_B.stop()    

    print("Done")
    # ZERO
    CURR_X=0
    CURR_Y=0

def cmdHome(robot):
    cmdPenUp(robot)
    cmdMoveStart(robot)

def processCommand(robot, cmd):
    global CURR_X, CURR_Y
    if len(cmd)>0:
        if cmd[0] == "PEN":
            if cmd[1] == "UP":
                cmdPenUp(robot)

            elif cmd[1] == "DOWN":
                cmdPenDown(robot)

            elif cmd[1] == "POINT":
                cmdPenDown(robot)
                cmdPenUp(robot)

            else:
                cmdPenMove(robot, int(cmd[1]))

        if cmd[0] == "ABS" and len(cmd)>2: #absolute position
            x=int(cmd[1])
            y=int(cmd[2])
            cmdAbs(robot, x, y)
        if cmd[0] == "MOVE" and len(cmd)>2: #relative position
            x=int(cmd[1])
            y=int(cmd[2])
            cmdMove(robot, x, y)

        if cmd[0] == "ROUND":
            cmdMove(robot, STEP_ROUND, 0)

        if cmd[0] == "START":
            cmdMoveStart(robot)

        if cmd[0] == "ZERO":
            CURR_X=0
            CURR_Y=0

        if cmd[0] == "POS":
            print("Current position: %i,%i" % (CURR_X, CURR_Y) )

robot.setMotorCallback(motorCallback)
robot.setSensorCallback(sensorCallback)

print("Start calibration?")
inp = six.moves.input("[Enter]")
print("Trank you")

cmdPenUp(robot)
cmdMoveStart(robot)

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
            continue

        if inp == "q":
            break

        if inp == "":
            inp = lastFile
        
        if not path.exists(inp):
            print("File not found: %s" % inp)
            continue

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
        cmdHome(robot)
        ##cmdAbs(robot, 0 ,0) #return home

finally:
    print("Goodbye")
    GPIO.cleanup()

