from pylgbst import *
from pylgbst.hub import MoveHub
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

#################################################################

def callback(color, distance):
    print("Stop")
    moving = False

robot.setSensorCallback(callback)

moving = False
try:
    while True:

        if robot.isButtonPressed(BTN_FORWARD):
            moving=True

        if robot.isButtonPressed(BTN_BACKWARD):
            moving = False

        dist = robot.getSensorDistance()
        if dist < 5 and moving:
            print("Stoppe")
            moving = False

        if moving:
            robot.motor_AB.angled(45,1)
            print("FORWARD")
        #sleep(0.1)

finally:
    robot.say("Goodbye")
    GPIO.cleanup()

