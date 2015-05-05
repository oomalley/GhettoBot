__author__ = 'oomadmin'

import MapTools
import navigation
import time

from GridMap import GridMap
from Sensors import mpu9150, Hcsr04
from MasterController import MasterController
from MotionController import Motor
from body import Body


imu = mpu9150()
prox = Hcsr04()
left_motor = Motor("P8_15", "P8_16", "P8_13")
right_motor = Motor("P8_9", "P8_10", "P9_16")
body = Body(prox, imu, left_motor, right_motor)
grid_map = GridMap()

master_controller = MasterController(body, grid_map)


#imu = Sensors.mpu9150()

#print("IMU started")

#while True:
    #print("Checking IMU")
    #print(imu)
    #time.sleep(1)


# obs = ((52,52),(53,52),(54,52))
#
# map = gmap.GridMap()
#
# for o in obs:
#     path = MapTools.get_LOF(map,o[0],o[1])
#     print (path)
#     map.UpdateObstical(path)

#mnode = gmap.MapNode(1,2)
#anode = navigation.AStarNode(3,4)
#tnode = navigation.AStarNode()
#tnode = mnode
#print(tnode.g)

#pathfinder = navigation.AStar(map, map.px,map.py, 53, 53)
#print( pathfinder.StartSearch())
