from Graph import Graph
from time import time
for i in range(0,100):
    try:
        H = Graph()
        H.generateRandomGraph()
        start2=time()
        p2,a2,c2,grph2=Graph.SuccessiveShortestPath(H)
        end2 = time()

        start=time()
        p,a,c,grp=Graph.CapacityScalingSuccessiveShortestPath(H)
        end = time()

         
        print end2-start2,"\t",end-start
    except:
        continue

