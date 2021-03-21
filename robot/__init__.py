# coding=utf-8
import hashlib
import os
import re
import subprocess
import time

from pylgbst import *
from pylgbst.hub import MoveHub
from pylgbst.peripherals import COLORS, COLOR_BLACK


import RPi.GPIO as GPIO

forward = FORWARD = right = RIGHT = 1
backward = BACKWARD = left = LEFT = -1
straight = STRAIGHT = 0

GPIO.setmode(GPIO.BCM)

VERNIE_TO_MOTOR_DEGREES = 1.3
VERNIE_SINGLE_MOVE = 430


class Robot(MoveHub):
    def __init__(self, conn):
        super(Robot, self).__init__(conn)

        while True:
            required_devices = (self.vision_sensor, self.motor_external)
            if None not in required_devices:
                break
            log.warn("Waiting for required devices to appear: %s", required_devices)
            time.sleep(1)
        self._head_position = 0
        self.motor_external.subscribe(self._external_motor_data)

        self._invert=True
        self._enableHead=True
        self._user_sensor_callback = None
        self._user_motor_callback = None

        self._sensor_distance = -1
        self.vision_sensor.subscribe(self._sensor_callback)

        #self._reset_head()
        self.say("ready.")
        time.sleep(1)

    def addButton(self, pin):
        log.warn("GPIO pin registered: %i", pin)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def isButtonPressed(self, pin):
        return not GPIO.input(pin)

    def say(self, phrase):
        print("%s" % phrase)

    def setInvert(self, inv):
        self._invert = inv

    def _external_motor_data(self, data):
        log.warn("External motor position: %s", data)
        self._head_position = data
        if self._user_motor_callback != None:
            self._user_motor_callback(data)

    def _sensor_callback(self, color, distance=None):
        log.warn("Color %s, distance %s", COLORS[color], distance)
        self._sensor_distance=distance
        if self._user_sensor_callback != None:
            self._user_sensor_callback(color, distance)

    def getSensorDistance(self):
        return self._sensor_distance

    def setSensorCallback(self, cb):
        self._user_sensor_callback = cb

    def setMotorCallback(self, cb):
        self._user_motor_callback = cb

    def color(self, color):
        self.led.set_color(color)

    def _reset_head(self):
        self.motor_external.timed(1, -0.2)
        #self.head(RIGHT, angle=45)

    def head(self, direction=RIGHT, angle=25, speed=0.1):
        if direction == STRAIGHT:
            angle = -self._head_position
            direction = 1

        self.motor_external.angled(direction * angle, speed)

    def turn(self, direction, degrees=90, speed=0.3):
        if self._enableHead:
            self.head(STRAIGHT, speed=0.5)
            self.head(direction, 35, 1)
        self.motor_AB.angled(int(VERNIE_TO_MOTOR_DEGREES * degrees), speed * direction, -speed * direction)
        if self._enableHead:
            self.head(STRAIGHT, speed=0.5)

    def turnaround(self):
        self.motor_AB.timed(0.8, -0.7, 0.7)

    def move(self, direction, distance=1, speed=0.2):
        if self._enableHead:
            self.head(STRAIGHT, speed=0.5)
        if self._invert:
            direction = direction * -1
        self.motor_AB.angled(distance * VERNIE_SINGLE_MOVE, speed * direction, speed * direction)

    def shot(self):
        self.motor_external.timed(0.5)
        if self._enableHead:
            self.head(STRAIGHT)
            self.head(STRAIGHT)

    def interpret_command(self, cmd, confirm):
        cmd = cmd.strip().lower().split(' ')
        if cmd[0] in ("head", "голова", "голову"):
            if cmd[-1] in ("right", "вправо", "направо"):
                confirm(cmd)
                self.head(RIGHT)
            elif cmd[-1] in ("left", "влево", "налево"):
                confirm(cmd)
                self.head(LEFT)
            else:
                confirm(cmd)
                self.head(STRAIGHT)
        elif cmd[0] in ("say", "скажи", "сказать"):
            if not cmd[1:]:
                self.say("text is empty")
                return
            say(' '.join(cmd[1:]))
        elif cmd[0] in ("fire", "shot", "огонь", "выстрел"):
            say("fire")
            self.shot()
        elif cmd[0] in ("end", "finish", "конец", "стоп"):
            self.say("finished")
            raise KeyboardInterrupt()
        elif cmd[0] in ("forward", "вперёд", "вперед"):
            try:
                dist = int(cmd[-1])
            except BaseException:
                dist = 1
            confirm(cmd)
            self.move(FORWARD, distance=dist)
        elif cmd[0] in ("backward", "назад"):
            try:
                dist = int(cmd[-1])
            except BaseException:
                dist = 1
            confirm(cmd)
            self.move(BACKWARD, distance=dist)
        elif cmd[0] in ("turn", "поворот", 'повернуть'):
            if cmd[-1] in ("right", "вправо", "направо"):
                confirm(cmd)
                self.turn(RIGHT)
            elif cmd[-1] in ("left", "влево", "налево"):
                confirm(cmd)
                self.turn(LEFT)
            else:
                confirm(cmd)
                self.turn(RIGHT, degrees=180)
        elif cmd[0] in ("right", "вправо", "направо"):
            confirm(cmd)
            self.turn(RIGHT)
        elif cmd[0] in ("left", "влево", "налево"):
            confirm(cmd)
            self.turn(LEFT)
        elif cmd[0]:
            self.say("Unknown command")
            self.say("commands help")
