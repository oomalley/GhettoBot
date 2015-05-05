__author__ = 'oisin'

from Queue import Queue
from threading import Thread
from time import sleep
from navigation import AStar
from MotionController import MotionController
from body import Body



class Objective(object):
    def __init__(self):
        self.completed = False
        pass

    "@property"
    def completed(self):
        return self.completed

    def done(self):
        self.completed = True


class PointObjective(Objective):
    def __init__(self, x, y):
        Objective.__init__(self)
        self.x = x
        self.y = y


class MasterController(object):
    def __init__(self, body, grid_map):
        self.body = body
        self.map = grid_map
        self.objective_queue = Queue()
        self.current_objective = None
        self.motion_controller = MotionController(self.body.left_motor, self.body.right_motor, self.body.inertial_sensor)

        # Add event hooks
        self.body.inertial_sensor.onMove += self.on_move
        self.body.inertial_sensor.onTilt += self.on_tilt
        self.body.inertial_sensor.onImpact += self.on_impact


        self.control_thread = Thread(target=self.master_control)
        self.control_thread.daemon = True
        self.control_thread.start()

    def add_objective(self, objective):
        if self.current_objective == None:
            self.current_objective == Objective
        else:
            self.objective_queue.put(Objective)

    def on_move(self, displacement):
        self.map.SetLocation(displacement[0], displacement[1])

    def on_tilt(self):
        pass

    def on_impact(self):
        pass

    def master_control(self):
        # AStar pathfinder = AStar()

        while True:
            if not self.current_objective.compleated:
                if isinstance(self.current_objective, PointObjective):
                    pass

            elif not self.objective_queue.empty():
                self.current_objective = self.objective_queue.get()

            else:
                sleep(1)
