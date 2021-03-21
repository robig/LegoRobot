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
robot.setInvert(False)

#################################################################

def callback(color, distance):
    global stop
    global moving
    if moving and distance < 7:
        print("Stop!")
        stop = True

robot.setSensorCallback(callback)

def startMotor():
    global robot
    global moving
    #robot.motor_AB.start_power(0.5, 0.5)
    robot.motor_AB.start_speed(0.5, 0.5)
    moving = True
    print("Start")

def stopMotor():
    global robot
    global moving
    global stop
    robot.motor_AB.stop()
    moving = False
    print("Stop")
    stop = False


moving = False
stop = False
try:
    while True:

        if not moving and robot.isButtonPressed(BTN_FORWARD):
            startMotor()

        if stop:
            robot.move(BACKWARD)
            robot.shot()
            robot.turnaround()
            robot.move(FORWARD)
            robot.move(FORWARD)
            

        if robot.isButtonPressed(BTN_BACKWARD):
            stopMotor()

        sleep(0.1)

finally:
    robot.say("Goodbye")
    GPIO.cleanup()

