__author__ = 'oomadmin'
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import threading
import Queue
import time
import datetime
import math
from EventHook import EventHook


class MotorCommand(object):
    def __init__(self, displacement):
        self.displacement = displacement

    "@property"
    def distance(self):
        return math.sqrt(math.pow(self.displacement[0], 2) + math.pow(self.displacement[1], 2))

    "@property"
    def direction(self):
        return math.atan2(self.displacement[1], self.displacement[0])


class Motor(object):
    def __init__(self, gpio1_id, gpio2_id, pwm_id):
        self.gpio1_id = gpio1_id
        self.gpio2_id = gpio2_id
        self.pwm_id = pwm_id
        self.onStall = EventHook()

        GPIO.setup(self.gpio1_id, GPIO.OUT)
        GPIO.setup(self.gpio2_id, GPIO.OUT)
        PWM.start(self.pwm_id, 100)

    def forward(self, throttle=100):
        GPIO.output(self.gpio1_id, GPIO.HIGH)
        GPIO.output(self.gpio2_id, GPIO.LOW)
        PWM.set_duty_cycle(self.pwm_id, throttle)

    def reverse(self, throttle=100):
        GPIO.output(self.gpio1_id, GPIO.LOW)
        GPIO.output(self.gpio2_id, GPIO.HIGH)
        PWM.set_duty_cycle(self.pwm_id, throttle)

    def halt(self):
        PWM.set_duty_cycle(self.pwm_id, 0)


class MotionController(object):

    # guestimate speed is 0.5m/s => 1m in 2s

    def __init__(self, motor_left, motor_right, imu):
        # self.speed = 0.5                                       # FixMe: need encoder to determine
        self.motor_left = motor_left
        self.motor_right = motor_right
        self.imu = imu
        self.command_queue = Queue.Queue()
        self.controller_thread = threading.Thread(target=self.motor_control)
        self.controller_thread.daemon = True
        self.controller_thread.start()

    def forward(self, distance):
        total_distance = 0
        p1 = [0, 0, 0]
        p2 = [0, 0, 0]

        self.motor_left.forward()
        self.motor_right.forward()

        while total_distance < distance:
            p1 = p2
            p2 = self.imu.displacement()
            delta = math.sqrt(math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2) + math.pow(p2[2] - p1[2], 2))
            total_distance += delta
            time.sleep(0.1)

    def turn(self, direction):
        while self.imu.read()[0] not in range(direction-5, direction+5):     # FixMe: issue with +/-180 degrees (gimble lock?)
            if self.imu.read()[0] > direction:
                # turn right
                self.motor_left.forward()
                self.motor_right.reverse()
            else:
                # turn left
                self.motor_left.reverse()
                self.motor_right.forward()
            time.sleep(0.1)

    def halt(self):
        self.motor_left.halt()
        self.motor_right.halt()

    def move(self, command):
        max_direction_deviation = 5
        total_distance = 0
        p1 = [0, 0, 0]
        p2 = [0, 0, 0]

        while total_distance < command.distance:
            p1 = p2
            p2 = self.imu.displacement()
            d_delta = math.sqrt(math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2) + math.pow(p2[2] - p1[2], 2))
            total_distance += d_delta

            a_delta = self.imu.bearing - command.direction # FixMe: seperate method

            if a_delta > max_direction_deviation:           # Turn Right
                while self.imu.bearing - command.direction > 0.80 * max_direction_deviation:
                    self.motor_left.forward()
                    self.motor_right.reverse()
                    time.sleep(0.05)

            elif a_delta < (max_direction_deviation * -1):  # Turn Left
                while self.imu.bearing - command.direction < -0.80 * max_direction_deviation:
                    self.motor_left.reverse()
                    self.motor_right.forward()
                    time.sleep(0.05)

            self.motor_left.forward()
            self.motor_right.forward()
            time.sleep(0.1)

    def set_waypoints(self, waypoints):
        self.command_queue.clear()
        self.command_queue.add(MotorCommand(waypoints[0]))
        last_waypoint = waypoints[0]
        displacement = [0, 0]
        for waypoint in waypoints[1:]:
            displacement[0] = waypoint[0] - last_waypoint[0]
            displacement[1] = waypoint[1] - last_waypoint[1]
            self.command_queue.add(MotorCommand(displacement))
            last_waypoint = waypoint

    def motor_control(self):                            # Fixme: should be event based
        while True:
            if self.command_queue.not_empty:
                command = self.command_queue.get()
                self.move(command)

            else:
                time.sleep(0.1)                         # wait for command



