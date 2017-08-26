from Edges import Edges
from Nodes import Nodes
from copy import copy
from copy import deepcopy
from numpy.random.mtrand import randint
import math
from time import time
from numpy.core.fromnumeric import mean
import psutil 
import resource
class Graph():
    def __init__(self):
        self.id = None
        self.nodes = []
        self.edges = []
    def addEdge(self, stN = None, enN=None,cp=None,capc=None):
        i = len(self.edges)
        self.edges.append(Edges(id=i,sN=stN,eN=enN,c=cp,capac=capc))
    def addNode(self,bcp=None):
        i = len(self.nodes)
        self.nodes.append(Nodes(id=i,bcap=bcp))
    def connect(self, sN, eN, EdgeId):
        self.nodes[sN].OutgoingEdges.append(self.edges[EdgeId])
        self.nodes[eN].IncomingEdges.append(self.edges[EdgeId])
        self.edges[EdgeId].sNode=self.nodes[sN]
        self.edges[EdgeId].eNode=self.nodes[eN]
    def getEdge(self,sN,en):
        for e in self.edges:
            if e.sNode is sN and e.eNode is en:
                return e
    def getEdgeById(self,id):
        for e in self.edges:
            if e.id == id:
                return e
    def getEdgeList(self,sN,en):
        edgeList=[]
        for e in self.edges:
            if e.sNode==sN and e.eNode==en:
                edgeList.append(e)
        return edgeList
    def getMinEdge(self,sN,eN):
        temp = 100000000000
        tempEdge=None
        for e in self.edges:
            if e.sNode==sN and e.eNode==eN:
                if e.costPi<temp:
                    temp =e.costPi
                    tempEdge=e
        return tempEdge
    def addResidualEdge(self,edg,cap):
        self.addEdge(edg.eNode,edg.sNode,edg.cost*-1,cap)
    def getEdgesSn(self,SN):
        eL=[]
        for e in self.edges:
            if e.sNode == SN:
                eL.append(e)
        return eL
    def getNodes(self,nodelist):
        nodeslist=[]
        for i in nodelist:
            for n in self.nodes:
                if i == n.id:
                    nodeslist.append(n)
        return nodeslist 
    def getResidual(self,arc):
        selected = None
        for e in self.edges:
            if e.sNode == arc.eNode and e.eNode==arc.sNode and e.cost == arc.cost*-1:
                selected=e
        return selected
    @staticmethod
    def resultPrinter(G,path,result,cost,flows=False):
        i=0
        for p in path:
            path1=[]
            i=i+1
            for k in p:
                path1.append(k.id)
            print i,": ",path1,"--> ",int(result[i-1])," (cost = ",int(cost[i-1]),")"
        print "Total Cost = ",sum(cost)
        if flows is True:
            print "id","\tSNode","\tENode","\tFlow"
            for e in G.edges:
                print e.id,"\t",e.sNode.id,"\t",e.eNode.id,"\t",e.flow 
        
    def createGraph(self, nodeNum,arcNum,snode, dnode,totalDemand,balanced=False):
        #Determining the per dnode and per snode b's for balanced version
        demval = int(math.floor(totalDemand/dnode))
        supmval = int(math.floor(totalDemand/snode))
        
        #Adding desired amount of nodes
        for i in range(0,nodeNum):
            self.addNode()
        
        #Supply Node Determination
        dt=deepcopy(totalDemand)
        t=0
        supplyIds=[]
        while t<snode:
            index=randint(0,nodeNum-1)
            if self.nodes[index].b is None:
                if t is not snode-1:
                    if balanced is True:
                        k=randint(math.floor(3*supmval/4),math.floor(supmval))
                    else:
                        k=randint(1,math.floor(dt-(snode-t)))
                    supplyIds.append(index)
                    self.nodes[index].b=k
                    dt = dt-k
                    t=t+1
                else:
                    self.nodes[index].b=dt
                    supplyIds.append(index)
                    t=t+1
            else:
                continue
         
        #Demand Node Determination   
        dt=deepcopy(totalDemand)
        t=0
        demandIds=[]
        while t<dnode :
            index=randint(0,nodeNum-1)
            if self.nodes[index].b is None:
                if t is not dnode-1:
                    if balanced is True:
                        k=randint(math.floor(3*demval/4),math.floor(demval))
                    else:
                        k=randint(1,math.floor(dt-(dnode-t)))
                    self.nodes[index].b=k*-1
                    demandIds.append(index)
                    dt = dt-k
                    t=t+1
                else:
                    self.nodes[index].b=dt*-1
                    demandIds.append(index)
                    t=t+1
            else:
                continue
        #Adding Edges From Each Supply Node to Each Demand Node to Guarantee the Connectivity
        arc=0
        for s in supplyIds:
            for d in demandIds:
                self.addEdge(self.nodes[s],self.nodes[d],50,self.nodes[s].b)
                arc=arc+1
        
        #Adding remaining arcs
        while arc<arcNum:
            index1=randint(0,nodeNum-1)
            index2=randint(0,nodeNum-1)      
            if self.getEdge(index1, index2) is None:
                if index1 is not index2: 
                    self.addEdge(self.nodes[index1],self.nodes[index2],randint(1,20),randint(0,totalDemand))
                    arc=arc+1
            else:
                continue
        #Adding dummy node and connecting all nodes to this node (Otherwise it may be problematic for capacity scaling due to possible loss of strong connectivity)
        self.addNode(0)
        dummy = self.nodes[len(self.nodes)-1]
        for i in self.nodes:
            if i is not dummy:
                self.addEdge(i, dummy, 2000, 1000000000000)
                self.addEdge(dummy, i, 2000, 1000000000000)
        #Setting remaining b's to 0 other than supply and demand nodes
        for n in self.nodes:
            if n.b is None:
                n.b=0
        
    def createCompleteGraph(self, nodeNum,snode, dnode,totalDemand):
        #Determining the per dnode and per snode b's for balanced version
        demval = int(math.floor(totalDemand/dnode))
        supmval = int(math.floor(totalDemand/snode))
        
        #Adding desired number of nodes
        for i in range(0,nodeNum):
            self.addNode()
        
        #Adding arc from each nodes to other nodes
        for s in self.nodes:
            for t in self.nodes:
                if s is not t:
                    if self.getEdge(s,t) is None:
                        self.addEdge(s, t, randint(0,20),totalDemand)
                        
        #Determining the supply nodes
        dt=deepcopy(totalDemand)
        t=0
        while t<snode:
            index=randint(0,nodeNum-1)
            if self.nodes[index].b is None:
                if t is not snode-1:
                    k=randint(1,t)
                    k=randint(0,math.floor(supmval))
                    self.nodes[index].b=k
                    dt = dt-k
                    t=t+1
                else:
                    self.nodes[index].b=dt
                    t=t+1
            else:
                continue
            
        #Determining the demand nodes
        dt=deepcopy(totalDemand)
        t=0
        while t<dnode :
            index=randint(0,nodeNum-1)
            if self.nodes[index].b is None:
                if t is not dnode-1:
                    k=randint(0,math.floor(demval))
                    self.nodes[index].b=k*-1
                    dt = dt-k
                    t=t+1
                else:
                    self.nodes[index].b=dt*-1
                    t=t+1
            else:
                continue
        #Setting remaining b's to 0
        for n in self.nodes:
            if n.b is None:
                n.b=0
    def generateRandomGraph(self):
        n = randint(0,50)
        m = randint(n,math.floor((n*(n-1)/2)-1))
        s = randint(1,math.floor(n/3))
        d = randint(1,math.floor(n/3))
        totalDemand = randint(s+d,1000)
        self.createGraph(n, m, s, d, totalDemand,False)
        
    @staticmethod
    def Djikstra(G,strt,end):
        #initialization
        s=[]
        s_bar=copy(G.nodes)
        node_num = len(G.nodes)
        distance=[]
        for i in range(0,node_num):
            if i==strt.id:
                distance.append(0)
            else:
                distance.append(10000000000)
        pred=[]
        for index in range(0,len(G.nodes)):
            pred.append(100000000000)
        #iterations begin
        while(len(s)<node_num):
            eList=[]
            for elem in s_bar:
                eList.append(elem.id)
            s_bar_distance=[]
            for k in s_bar:
                s_bar_distance.append(distance[k.id])
            
            chosen = eList[s_bar_distance.index(min(s_bar_distance))]
            s.append(G.nodes[chosen])
            s_bar.remove(G.nodes[chosen])
            if len(G.getEdgesSn(G.nodes[chosen]))==0:
                break
            else:
                for ed in G.getEdgesSn(G.nodes[chosen]):
                    if distance[ed.eNode.id]>distance[ed.sNode.id]+ed.costPi:
                        distance[ed.eNode.id]=distance[ed.sNode.id]+ed.costPi
                        pred[ed.eNode.id]=ed.sNode.id   
        #determining the path from s to t 
        t=end.id
        pth=[]
        pth.append(t)
        try:
            while(t is not strt.id):
                pth.append(pred[t])
                t=pred[t]
            q=reversed(pth)  
            t = list(q)
        except:
            t=False
        return(t,distance)
    
    @staticmethod      
    def SuccessiveShortestPath(I):
        #initialization
        G = deepcopy(I)
        E=[]
        D=[]
        for n in G.nodes:
            n.e = n.b
            if n.e>0:
                E.append(n)
            elif n.e<0:
                D.append(n)
            else:
                continue
        paths = []
        amount= []
        flowCosts = []
        for n in G.nodes:
            n.pi = 0
        #iterations begin
        while len(E)>0:
            #copying the graph instance to prepare for djikstra
            K = deepcopy(G)
            removingList=[]
            for m in K.edges:
                if m.capacity < 1:
                    removingList.append(m)
            for i in removingList:
                K.edges.remove(i)
            #trying all possible demand and supply choice in djikstra in case of fail  
            for sup in range(0,len(E)):
                for dem in range(0,len(D)):
                    k=E[sup]
                    l=D[dem]
                    path,costs=Graph.Djikstra(K,k,l)
                    if path is not False:
                        break
                if path is not False:
                    break
            if path is False:
                break
            originalpath = G.getNodes(path)
            path = K.getNodes(path)
            #updating pi values
            for i in G.nodes:
                i.pi = i.pi - costs[i.id]
            #deterimining the flow amount
            delta=1000000000
            for i in range(0,len(path)-1):
                if delta > K.getMinEdge(path[i],path[i+1]).capacity:
                    delta = K.getMinEdge(path[i],path[i+1]).capacity
            if delta > k.e:
                delta=k.e
            if delta > -1*l.e:
                delta = -1*l.e

            originalpath[0].e = originalpath[0].e-delta
            originalpath[len(path)-1].e=originalpath[len(path)-1].e+delta 
            #updating the edges and residuals
            cost = 0
            for i in range(0,len(path)-1):
                ed = G.getEdgeById(K.getMinEdge(path[i],path[i+1]).id)
                ed.capacity = ed.capacity - delta
                ed.flow = ed.flow+delta
                cost=cost+delta*ed.cost
            flowCosts.append(cost)
            #Update Residual
            for i in range(0,len(path)-1):
                current = G.getEdgeById(K.getMinEdge(path[i],path[i+1]).id)
                residual = G.getResidual(current)
                if residual is not None:
                    residual.capacity = residual.capacity + delta
                else:
                    G.addResidualEdge(current,delta)
                    G.getResidual(current).costPi=current.costPi
            #updating the pi costs
            for e in G.edges:
                e.costPi=e.cost-e.sNode.pi+e.eNode.pi
                
            paths.append(originalpath)
            amount.append(delta)
            
            #choosing the supply and demand
            E=[]
            D=[]
            for n in G.nodes:
                if n.e>0:
                    E.append(n)
                elif n.e<0:
                    D.append(n)
                else:
                    continue
        return paths,amount,flowCosts,G
    @staticmethod      
    def CapacityScalingSuccessiveShortestPath(I):
        G = deepcopy(I)
        #Scaling Adjustments and Initialization
        maxNode=None
        maxCapacity=0
        for n in G.nodes:
            if n.b > maxCapacity:
                maxCapacity = n.b
                maxNode = n
        DELTA = pow(2,math.floor(math.log(maxCapacity)/math.log(2)))
        
        for n in G.nodes:
            n.pi = 0
        for n in G.nodes:
            n.e = n.b
            
        paths=[]
        amount = []
        flowCosts = []
        while DELTA >=1:
            #optimality condition check and correction
            residualToAdd=[]
            for e in G.edges:
                if e.capacity>=DELTA and e.costPi<0:
                    residualToAdd.append(e)
            for e in residualToAdd:
                tp=[]
                tp.append(e.sNode)
                tp.append(e.eNode)
                path = tp
                paths.append(path)
                amount.append(e.capacity)
                e.sNode.e=e.sNode.e-e.capacity
                e.eNode.e=e.eNode.e+e.capacity
                flowCosts.append(e.capacity*e.cost)
                e.flow = e.flow+e.capacity
                residual = G.getResidual(e)
                e.costPi=e.cost-e.sNode.pi + e.eNode.pi
                if residual is not None:
                    residual.capacity = residual.capacity + e.capacity
                    residual.costPi = residual.cost-residual.sNode.pi+residual.eNode.pi
                else:
                    G.addResidualEdge(e,e.capacity)
                    G.getResidual(e).costPi=G.getResidual(e).cost -G.getResidual(e).sNode.pi+G.getResidual(e).eNode.pi
                e.capacity=0
            #Determination of the supply and deman sets
            E=[]
            D=[]
            for n in G.nodes:
                if n.e>=DELTA:
                    E.append(n)
                elif n.e<=-1*DELTA:
                    D.append(n)
                else:
                    continue

            while len(E)>0 and len(D)>0:
                #Preparation for djikstra
                K = deepcopy(G)
                removingList=[]
                for m in K.edges:
                    if m.capacity < DELTA:
                        removingList.append(m)
                for i in removingList:
                    K.edges.remove(i)
                #trying all combination of the set in case of problematic choice
                for sup in range(0,len(E)):
                    for dem in range(0,len(D)):
                        k=E[sup]
                        l=D[dem]
                        path,costs=Graph.Djikstra(K,k,l)
                        if path is not False:
                            break
                    if path is not False:
                        break
                if path is False:
                    break
                originalpath=G.getNodes(path)
                path = K.getNodes(path)
                #updating pi values
                for i in G.nodes:
                    i.pi = i.pi - costs[i.id]
                
                delta=DELTA
    
                originalpath[0].e =originalpath[0].e-delta
                originalpath[len(path)-1].e=originalpath[len(path)-1].e+delta 
                
                #updating residual and arc capacities
                cost=0
                for i in range(0,len(path)-1):
                    temp = G.getEdgeById(K.getMinEdge(path[i],path[i+1]).id)
                    temp.capacity = temp.capacity - delta
                    temp.flow = temp.flow+delta
                    cost = cost+delta*temp.cost
                flowCosts.append(cost)
                for i in range(0,len(path)-1):
                    current = G.getEdgeById(K.getMinEdge(path[i],path[i+1]).id)
                    residual = G.getResidual(current)
                    if residual is not None:
                        residual.capacity = residual.capacity + delta
                    else:
                        G.addResidualEdge(current,delta)
                #updating pi costs
                for e in G.edges:
                    e.costPi=e.cost-e.sNode.pi+e.eNode.pi
                paths.append(originalpath)
                amount.append(delta)
                #determining the E and D sets
                E=[]
                D=[]
                for n in G.nodes:
                    if n.e>=DELTA:
                        E.append(n)
                    elif n.e<=-1*DELTA:
                        D.append(n)
                    else:
                        continue
            #update of the scaling delta
            DELTA=DELTA/2
        return paths,amount,flowCosts,G
        
        
        
        
#A=Graph()
#A.addNode(bcp=10)
#A.addNode(bcp=-3)
#A.addNode(bcp=-7)
#A.addNode(bcp=13)
#A.addNode(bcp=-13)
#A.addEdge(A.nodes[0],A.nodes[1],1,100)
#A.addEdge(A.nodes[0],A.nodes[3],1,23)
#A.addEdge(A.nodes[3],A.nodes[4],1,42)
#A.addEdge(A.nodes[4],A.nodes[2],1,10)
#A.addEdge(A.nodes[3],A.nodes[1],1,100)

# C=Graph()
# C.addNode(4)
# C.addNode(0)
# C.addNode(0)
# C.addNode(-4)
# C.addEdge(C.nodes[0],C.nodes[1],2,4)
# C.addEdge(C.nodes[0],C.nodes[2],2,2)
# C.addEdge(C.nodes[1],C.nodes[2],1,2)
# C.addEdge(C.nodes[1],C.nodes[3],3,3)
# C.addEdge(C.nodes[2],C.nodes[3],1,5)
# 
# D=Graph()
# D.addNode(7)
# D.addNode(1)
# D.addNode(0)
# D.addNode(0)
# D.addNode(-1)
# D.addNode(-7)
# D.addEdge(D.nodes[0],D.nodes[1],2,4)
# D.addEdge(D.nodes[0],D.nodes[2],5,3)
# D.addEdge(D.nodes[1],D.nodes[3],3,8)
# D.addEdge(D.nodes[2],D.nodes[1],7,1)
# D.addEdge(D.nodes[2],D.nodes[4],2,3)
# D.addEdge(D.nodes[3],D.nodes[4],1,2)
# D.addEdge(D.nodes[3],D.nodes[5],4,5)
# D.addEdge(D.nodes[4],D.nodes[1],5,2)
# D.addEdge(D.nodes[4],D.nodes[5],3,3)



# print "\nSuccessive Shortest Path"
# start2=time()
# p2,a2,c2=Graph.SuccessiveShortestPath(C)
# end2 = time()
# print "Execution Time:",end2-start2 
# Graph.resultPrinter(C, p2, a2,c2)
#  
#  
#  
#  
# print "\nCapacity Scaling Successive Shortest Path"
# start=time()
# p,a,c=Graph.CapacityScalingSuccessiveShortestPath(C)
# end = time()
# print "Execution Time:",end-start 
# Graph.resultPrinter(C, p, a,c)


# a=[]
# for i in range(0,5):
#     a.append(100+i*50)
# for k in a:
#     sspTime=[]
#     cssspTime=[] 
#     for i in range(0,1):
#         B=Graph()
#         B.createGraph(50,80,5,1,k,False)
#             
#         #print "Successive Shortest Path"
#         start2=time()
#         p2,a2,c2,grph2=Graph.SuccessiveShortestPath(B)
#         end2 = time()
#         #print "Execution Time:",end2-start2
#         sspTime.append(end2-start2) 
#         #Graph.resultPrinter(grph2, p2, a2,c2)
#             
#             
#         #print "\nCapacity Scaling Successive Shortest Path"
#         start=time()
#         p,a,c,grp=Graph.CapacityScalingSuccessiveShortestPath(B)
#         end = time()
#         #print "Execution Time:",end-start 
#         cssspTime.append(end-start)
#         #Graph.resultPrinter(grp, p, a,c)
#     print "50/80/5/1/",k,"\t",mean(sspTime),"\t",mean(cssspTime)

 
# B=Graph()
# B.createGraph(100,7000,10,10,100,False)
#   
# print "Successive Shortest Path"
# start2=time()
# p2,a2,c2,grph2=Graph.SuccessiveShortestPath(B)
# end2 = time()
# print "Execution Time:",end2-start2
# Graph.resultPrinter(grph2, p2, a2,c2,False)
#   
#   
# print "\nCapacity Scaling Successive Shortest Path"
# start=time()
# p,a,c,grp=Graph.CapacityScalingSuccessiveShortestPath(B)
# end = time()
# print "Execution Time:",end-start 
# Graph.resultPrinter(grp, p, a,c,False)


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



