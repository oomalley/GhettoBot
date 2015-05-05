__author__ = 'oomadmin'
import math

def get_LOF(Map, x2, y2):

    x1,y1 = Map.GetLocation()

    points = []
    issteep = abs(y2-y1) > abs(x2-x1)
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        rev = True
    deltax = x2 - x1
    deltay = abs(y2-y1)
    error = int(deltax / 2)
    y = y1
    ystep = None
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(x1, x2 + 1):
        if issteep:
            points.append((y, x))
        else:
            points.append((x, y))
        error -= deltay
        if error < 0:
            y += ystep
            error += deltax
    # Reverse the list if the coordinates were reversed
    if rev:
        points.reverse()
    return points

def ToPolar(x,y):
    return math.sqrt(x*x+y*y), math.degrees(math.atan(y/x))

def ToCartesian(r,d):
    return r*math.cos(d), r*math.sin(d)

def Dist(Map, x0, y0, x1, y1):
    return math.sqrt(math.pow((x1-x0) * Map.GetNodeSize(), 2) + math.pow((y1-y0) * Map.GetNodeSize(), 2))

def OrthDist(Map, x0, y0, x1, y1):
    return (abs(x1 - x0) * Map.GetNodeSize() + abs(y1 - y0) * Map.GetNodeSize())