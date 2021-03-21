from pylgbst import *
from pylgbst.hub import MoveHub
from pylgbst.peripherals import *
from robot import *
from time import sleep

BTN_FORWARD=19
BTN_BACKWARD=26

logging.basicConfig(level = logging.WARN)
log = logging.getLogger("test")

mac="00:16:53:B2:30:37"
conn = get_connection_bluegiga(hub_mac=mac)

print("Connected.")

robot = Robot(conn)
robot.addButton(BTN_BACKWARD)
robot.addButton(BTN_FORWARD)
robot.setInvert(False)

#################################################################
moving = False
isWhite = False
isRed = False

def callback(color, distance):
    print(color)

    global isRed
    global isWhite
    if color == COLOR_RED:
        isRed=True
        isWhite = False
    elif color == COLOR_WHITE:
        isWhite = True
        isRed = False
    else:
        isRed = False
        isWhite = False

robot.setSensorCallback(callback)

try:
    while True:

        if robot.isButtonPressed(BTN_FORWARD):
            moving=True

        if robot.isButtonPressed(BTN_BACKWARD):
            moving = False


        step=0.2
        if moving:
            if isRed:
                robot.motor_AB.timed(step, 0.7, -0.3)
                robot.motor_AB.timed(step, 0.5) # FORWARD
                #robot.turn(LEFT)
            elif isWhite:
                robot.motor_AB.timed(step, -0.3, 0.7)
                robot.motor_AB.timed(step, 0.5) # FORWARD
                #robot.turn(RIGHT)
            else:
                robot.motor_AB.timed(step, 0.5)
                print("FORWARD")

        sleep(0.1)

finally:
    robot.say("Goodbye")
    GPIO.cleanup()

