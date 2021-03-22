from pylgbst import *
from pylgbst.hub import MoveHub
from robot import *
from time import sleep

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

STEP_X=20
STEP_Y=20
STEP_Z=10

def motorCallback(pos):
    print(pos)

robot.setMotorCallback(motorCallback)

readCommands('plot1.csv')

direction = 0
try:
    while running:

        if robot.isButtonPressed(BTN_BACKWARD):
            print("UP")
            direction = UP

        if direction == UP:
            robot.motor_external.angled(STEP_Z, 0.3)
            #robot.motor_B.angled(STEP_X, 0.3)
            robot.motor_A.angled(STEP_Y, 0.3)

        if robot.isButtonPressed(BTN_FORWARD):
            direction = DOWN

        if direction == DOWN:
            robot.motor_external.angled(STEP_Z, -0.3)
            #robot.motor_B.angled(STEP_X, -0.3)
            robot.motor_A.angled(STEP_Y, -0.3)
            #running = False

        if robot.isButtonPressed(BTN_LEFT):
            direction = 0

        sleep(0.1)

finally:
    robot.say("Goodbye")
    GPIO.cleanup()

