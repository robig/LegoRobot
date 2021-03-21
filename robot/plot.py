from robot import *

def colorCallback(color, distance):
    print("Color")

def motorCallback(data):
    print("Motor")

plotInstance = None

class Plot(Robot):
    def __init__(self, conn):
        super(Plot, self).__init__(conn)

        self.setSensorCallback(colorCallback)
        self.setMotorCallback(motorCallback)
        plotInstance = self
    
    def allZero(self):
        print("To 0,0")