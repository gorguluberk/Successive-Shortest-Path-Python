from Nodes import Nodes
class Edges():
    def __init__(self, id,eN=None,sN=None,c=None,capac=None):
        self.id = id
        self.sNode = sN
        self.eNode = eN
        self.cost = c
        self.capacity = capac
        self.costPi = c
        self.flow = 0
        

