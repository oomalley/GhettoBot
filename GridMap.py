
class MapNode(object):
    # FixMe: redo a 2D linked list
    unknown = 0
    clear = 1
    impassable = -1

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.terrain = MapNode.unknown

    @property
    def x(self):
        return self.x
    @property
    def y(self):
        return self.y

    @property
    def terrain(self):
        return self.terrain

    @terrain.setter
    def terrain(self, terrain):
        self.terrain = terrain      # FixMe: Validate arg!!

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def __str__(self):
        return str("(" + self.x + "," + self.y + ")")

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class GridMap():

    def __init__(self):
        self.nodes = [[MapNode(x, y) for y in range(101)] for x in range(101)]
        self.nodesize = 100     # mm
        self.x0 = 50
        self.y0 = 50
        self.px = self.x0
        self.py = self.y0

    def GetNodeSize(self):
        return self.nodesize

    def SetNode(self, x, y, TerrainType):
        self.nodes[x][y].terrain = TerrainType

    def getnode(self, x, y):
        return self.nodes[x][y]

    def GetLocation(self):
        return self.px, self.py

    def SetLocation(self, x, y):
        px = self.x0 + (x % self.nodesize)
        py = self.y0 + (y % self.nodesize)

    def UpdateClear(self, path):
        for node in path:
            self.SetNode(node[0], node[1], MapNode.clear)

    def UpdateObstical(self, path):
        self.UpdateClear(path[:-1])
        self.SetNode(path[-1][0], path[-1][1], MapNode.impassable)

    def GetAdjacent(self, MapNode):
        AdjNodes = []

        if MapNode.y > 0:                                                         # Bottom Node
            if self.nodes[MapNode.x][MapNode.y - 1].terrain != MapNode.impassable:
                AdjNodes.append(self.nodes[MapNode.x][MapNode.y - 1])

        if MapNode.y > 0 and MapNode.x > 0:                                       # Bottom Left Node
            if self.nodes[MapNode.x - 1][MapNode.y - 1].terrain != MapNode.impassable:
                AdjNodes.append(self.nodes[MapNode.x - 1][MapNode.y - 1])

        if MapNode.y > 0 and MapNode.x < len(self.nodes) - 1:                     # Bottom Right Node
            if self.nodes[MapNode.x + 1][MapNode.y - 1].terrain != MapNode.impassable:
                AdjNodes.append(self.nodes[MapNode.x + 1][MapNode.y - 1])

        if MapNode.x > 0:                                                         # Left Node
            if self.nodes[MapNode.x - 1][MapNode.y].terrain != MapNode.impassable:
                AdjNodes.append(self.nodes[MapNode.x - 1][MapNode.y])

        if MapNode.x < len(self.nodes) - 1:                                       # Right Node
            if self.nodes[MapNode.x+1][MapNode.y].terrain != MapNode.impassable:
                AdjNodes.append(self.nodes[MapNode.x+1][MapNode.y])

        if MapNode.y < len(self.nodes[0]) - 1:                                    # Top Node
            if self.nodes[MapNode.x][MapNode.y + 1].terrain != MapNode.impassable:
                AdjNodes.append(self.nodes[MapNode.x][MapNode.y + 1])

        if MapNode.x > 0 and MapNode.y < len(self.nodes[0]) - 1:                  # Top Left Node
            if self.nodes[MapNode.x - 1][MapNode.y + 1].terrain != MapNode.impassable:
                AdjNodes.append(self.nodes[MapNode.x - 1][MapNode.y + 1])

        if MapNode.x < len(self.nodes) - 1 and MapNode.y < len(self.nodes[0]) - 1:  # Top Right Node
            if self.nodes[MapNode.x + 1][MapNode.y + 1].terrain != MapNode.impassable:
                AdjNodes.append(self.nodes[MapNode.x + 1][MapNode.y + 1])

        return AdjNodes