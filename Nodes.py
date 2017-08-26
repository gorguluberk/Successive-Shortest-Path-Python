class Nodes():
    def __init__(self,id,bcap=None):
        self.id = id
        self.IncomingEdges = []
        self.OutgoingEdges = []
        self.b = bcap
        self.e =None
        self.pi=None

