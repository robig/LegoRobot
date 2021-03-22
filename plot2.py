from pylgbst import *
from pylgbst.hub import MoveHub
from robot import *
from time import sleep
from csv import reader

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
STEP_Y=20
STEP_Z=10
SPEED_X=SPEED_Y=0.3

CURR_X = CURR_Y = 0
CURR_CMD = 0

def motorCallback(pos):
    print(pos)

def readCommands(filename):
    with open(filename, 'r') as read_obj:
        csv_reader = reader(read_obj)
        ret = []
        for row in csv_reader:
            # row variable is a list that represents a row in csv
            print(row)
            ret.append(row)
        return ret
    return []

robot.setMotorCallback(motorCallback)

print("Reading commands from file...")
commands = readCommands('plot2.csv')
print(" %i commands read", len(commands))

try:
    while running and CURR_CMD < len(commands):

        if robot.isButtonPressed(BTN_BACKWARD):
            processing = not(processing)
            if processing:
                print("Starting...")
            else:
                print("Paused.")


        cmd = commands[CURR_CMD]
        if processing and len(cmd)>0:

            if cmd[0] == "PEN" and cmd[1] == "UP":
                print("* Pen up")
                robot.motor_external.angled(STEP_Z, 0.3)
                #robot.motor_B.angled(STEP_X, 0.3)
                #robot.motor_A.angled(STEP_Y, 0.3)

            if cmd[0] == "PEN" and cmd[1] == "DOWN":
                print("* Pen down")
                robot.motor_external.angled(STEP_Z, -0.3)
                #robot.motor_B.angled(STEP_X, -0.3)
                #robot.motor_A.angled(STEP_Y, -0.3)

            if cmd[0] == "ABS" and len(cmd)>2: #absolute position
                print("* Move to %s,%s", cmd[1], cmd[2])
                x=int(cmd[1])
                y=int(cmd[2])
                diff_x=CURR_X - x
                diff_y=CURR_Y - y
                if diff_x != 0:
                    robot.motor_B.angled(diff_x * STEP_X, SPEED_X)
                if diff_y != 0:
                    robot.motor_A.angled(diff_y * STEP_Y, SPEED_Y)
                CURR_X=x
                CURR_Y=y
            if cmd[0] == "MOVE" and len(cmd)>2: #relative position
                print("* Move +%s,+%s", cmd[1], cmd[2])
                x=int(cmd[1])
                y=int(cmd[2])
                if x != 0:
                    robot.motor_B.angled(x * STEP_X, SPEED_X)
                if y != 0:
                    robot.motor_A.angled(y * STEP_Y, SPEED_Y)
                CURR_X=CURR_X+x
                CURR_Y=CURR_Y+y

        if processing:
            CURR_CMD=CURR_CMD+1

        sleep(0.1)

finally:
    robot.say("Goodbye")
    GPIO.cleanup()

