__author__ = 'oomadmin'
import MapTools
import GridMap
import operator

class AStarNode(GridMap.MapNode):
    def __init__(self,x=0,y=0, h=0):
        GridMap.MapNode.__init__(self, x, y)
        #self.x = x
        #self.y = y
        #self.reachable = reachable
        self.g = 0
        self.h = h
        self.f = h
        self.parent = None

    "@property"
    def g(self):
        return self.g

    "@property"
    def h(self):
        return self.h

    "@property"
    def f(self):
        return self.f

    def Update(self, G, AStarNode, GridMap):
        self.g = G + GridMap.nodesize
        # self.h = MapTools.OrthDist(GridMap,self.x,self.y, AStarNode.x, AStarNode.y)
        self.f = self.g + self.h

    def SetHeuristic(self, H):
        self.h = H
        self.f = self.g + self.h


class AStar(object):
    def __init__(self, GridMap, x0, y0, x1, y1):
        self.map = GridMap
        self.AStarNodes = []
        self.start = AStarNode(x0,y0)
        self.end = AStarNode(x1,y1)
        self.lastchecked = self.start

    def GetHeuristic(self, cell):
        return MapTools.OrthDist(self.map, cell.x, cell.y, self.end.x, self.end.y)

    def GetAdjacentNodes(self, Node):
        AdjNodes = []
        for node in self.map.GetAdjacent(Node):
            # TempNode = AStarNode()
            for anode in self.AStarNodes:
                if(node.x == anode.x and node.y == anode.y):
                    #print ("Retreved AStarNode("+ str(node.x) +"," + str(node.y) +")")
                    AdjNodes.append(anode)
                    break
            else:
                # print("Adding new AStarNode("+ str(node.x) +"," + str(node.y) +")")
                TempNode = AStarNode(node.x, node.y, self.GetHeuristic(node))
                AdjNodes.append(TempNode)
                self.AStarNodes.append(TempNode)
        return AdjNodes

    def search(self, AStarNode, Depth):
        self.lastchecked = AStarNode
        Path = []

        if AStarNode == self.end:
            Path.append(AStarNode)
            return Path
        elif Depth <= 0:
            print("Too Deep")
            return []

        AdjNodes = self.GetAdjacentNodes(AStarNode)
        try:
            AdjNodes.remove(self.lastchecked)
        except ValueError:
            pass
        AdjNodes.sort(key=operator.attrgetter('f'))

        for AdjNode in AdjNodes:
            if(AdjNode.g > AStarNode.g + self.map.nodesize or AdjNode.g == 0):
                AdjNode.Update(AStarNode.g, self.end, self.map)
                # print("Searching("+str(AdjNode.x) + "," + str(AdjNode.y) +") from ("+str(AStarNode.x)+","+str(AStarNode.y)+"): g=" + str(AdjNode.g))
                NewPath = self.search(AdjNode, Depth - 1)
                if(len(NewPath) > 0):
                    print(NewPath)
                    NewPath.append(AStarNode)
                    return NewPath
        else:
            # print("Dead End")
            return []

    def start_search(self):
        # Fixme: reverse returned  array
        return self.search(self.start,10)
