from pylgbst import *
from pylgbst.peripherals import VisionSensor
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
running = True
criterion = min

cur_luminosity = 0


def on_change_lum(lumn, unknown):
    del unknown
    global cur_luminosity
    cur_luminosity = lumn


lum_values = {}


def on_btn(pressed):
    global running
    if pressed:
        running = False


def on_turn(angl):
    lum_values[angl] = cur_luminosity


robot.button.subscribe(on_btn)
robot.vision_sensor.subscribe(on_change_lum, VisionSensor.DEBUG, granularity=1)
robot.motor_A.subscribe(on_turn, granularity=30)

# TODO: add bump detect to go back?

while running:
    # turn around, measuring luminosity
    lum_values = {}
    robot.turn(RIGHT, degrees=360, speed=0.2)

    # get max luminosity angle
    amin = min(lum_values.keys())
    lmax = max(lum_values.values())
    almax = amin
    for almax in lum_values:
        if lum_values[almax] == lmax:
            break

    angle = int((almax - amin) / VERNIE_TO_MOTOR_DEGREES)
    logging.info("Angle to brightest %.3f is %s", lmax, angle)

    # turn towards light
    if angle > 180:
        robot.turn(LEFT, degrees=360 - angle)
    else:
        robot.turn(RIGHT, degrees=angle)

    # Now let's move until luminosity changes
    lum = cur_luminosity
    while cur_luminosity >= lum:
        logging.info("Luminosity is %.3f, moving towards it", cur_luminosity)
        robot.move(FORWARD, 1)

robot.vision_sensor.unsubscribe(on_change_lum)
robot.button.unsubscribe(on_btn)