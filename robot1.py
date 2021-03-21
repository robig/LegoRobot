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

robot.move(FORWARD)
robot.turn(RIGHT)
robot.move(FORWARD)
robot.turn(LEFT)
robot.move(BACKWARD)

