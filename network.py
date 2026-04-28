import numpy.linalg as vec
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import LineCollection
import random as rand

# CLASSES #################### 
class Node:
  
  def __init__(self , pos : list[float] , charge : float = 1 , vel: list[float] = None ):
    self.pos    : np.typing.NDArray[np.float64]  = np.array([pos[0],pos[1]])
    self.charge : float                          = charge
    self.connections = {}
    self.vel    : np.typing.NDArray[np.float64]  = np.array([0.0,0.0]) if vel is None else np.array([vel[0],vel[1]])
    self.mass                                    = 1
    
class Edge:
  
  def __init__(self, node1: Node, node2: Node, k : float = 1):
    if node2 in node1.connections:
      raise AttributeError("Edge already exists")
    else:
      self.connects            = frozenset([node1,node2])
      self.k                   = k
      node1.connections[node2] = self
      node2.connections[node1] = self

class Network:
 
  def __init__(self):
    self.nodes : list[Node] = []
    self.edges : list[Edge] = []

  
  def addNode(self,node : Node):
    self.nodes.append(node)
    return node
    
  def addNodes(self,nodeList : list[Node]):
    for node in nodeList:
      self.nodes.append(node)
    
  def removeNode(self,node : Node):
    if node in self.nodes:
      self.nodes.remove(node)
      
  def addEdge(self,edge : Edge):
    self.edges.append(edge)
    
  def addEdges(self,edgelist : list[Edge]):
    for edge in edgelist:
      self.edges.append(edge)
    
  def removeEdge(self,edge : Edge):
    if edge in self.edges:
      self.edges.remove(edge)
      
  def getPositions(self):
    positionArray = np.array([node.pos for node in self.nodes])
    return positionArray

  def getVelocities(self):
    velocityArray = np.array([node.vel for node in self.nodes])
    return velocityArray
  
  def getMaxVelocity(self):
    velocities = vec.norm(self.getVelocities())
    return velocities.max()
  
  def getLinePairs(self):
    edgelist = []
    for edge in self.edges:
      pointlist = []
      for node in edge.connects:
        pointlist.append(node.pos)
      edgelist.append(np.array(pointlist))
    return np.array(edgelist)
  
  def setMasses(self):
    for node in self.nodes:
      length = len(node.connections)
      node.mass = length if length > 0 else 200
      
  def addRandomNode(self, coordRange : float = 5, chargeRange : float = 1.0):
    x = 2*coordRange * np.random.rand() - coordRange
    y = 2*coordRange * np.random.rand() - coordRange
    if chargeRange == 1.0:
      node = Node([x,y])
    else:
      q = chargeRange * np.random.rand()
      node = Node(pos = [x,y], charge = q)
    self.nodes.append(node)
    return node
  
  def addRandomEdge(self):
    n = len(self.nodes)
    trying = True
    if len(self.edges) >= (n * (n-1) )/ 2:
      trying = False
      print("Failed to make edge, too many exist for the number of nodes")
    else:
      while trying is True:
        i = np.random.randint(0,len(self.nodes))
        j = np.random.randint(0,len(self.nodes))
        if i != j and self.nodes[i] not in self.nodes[j].connections:
          edge = Edge(self.nodes[i],self.nodes[j])
          self.addEdge(edge)
          trying = False
          return edge
    
# FUNCTIONS #################### 

# Calculate the force between particles using Coulomb's Law
def calcChargeForce(node1 : Node , node2 : Node):
  q1 = node1.charge
  q2 = node2.charge
  
  # r is in the direction pointing from 
  r  = node1.pos - node2.pos
  distance = vec.norm(r)
  if vec.norm(r) > 0:
    return ( (q1*q2) / (distance ** 3) ) * r
  else:
    return np.array([0,0])
   
# Calculate the force from a connection using F = -kx
def calcSpringForce( node1: Node, node2: Node):
  if node2 in node1.connections:
    spring : Edge = node1.connections[node2]
    k = spring.k
    
    # r points from node2 to node 1
    r     = node1.pos - node2.pos
    
    # Force pulling on node1
    force = -k * r
    
    return force
  else:
    return np.array([0,0])

# Create (antisymmetric) matrix of forces from charge
def makeChargeMatrix(nodes: list):
  
  # create a matrix of the proper size, default zeros since that's what the diagonals will be
  forceMatrix = np.zeros((len(nodes),len(nodes),2))
      
  for i in range(len(nodes)):
    for j in range(i+1,len(nodes)):
      force = calcChargeForce(nodes[i],nodes[j])
      forceMatrix[i,j] = force
      forceMatrix[j,i] = -force
  
  return forceMatrix

# Create antisymmetric matrix of forces from springs
def makeSpringMatrix(nodes: list[Node]):
  
  # create a matrix of the proper size, default zeros since that's what the diagonals will be
  forceMatrix = np.zeros((len(nodes),len(nodes),2))
      
  for i in range(len(nodes)):
    for j in range(i+1,len(nodes)):
      force = calcSpringForce(nodes[i],nodes[j])
      forceMatrix[i,j] = force
      forceMatrix[j,i] = -force
  
  return forceMatrix

# Add the two types of force matrices
def makeForceMatrix(nodes: list[Node]):
  return makeChargeMatrix(nodes) + makeSpringMatrix(nodes)
  
# This outputs an array of (x,y) pairs where the ith value corresponds
# to the forces on the ith node in "nodes"
def summedForces(nodes : list[Node]):

  forces = np.sum( makeForceMatrix(nodes) , axis = 1)
  
  return forces
  
def updateNodes(nodes : list[Node], timestep : float, damping : float = 0.5):
  summed = summedForces(nodes)
  # F = ma baby
  for i in range(len(nodes)):
    nodes[i].pos = nodes[i].pos + nodes[i].vel * timestep
    nodes[i].vel = damping*(nodes[i].vel + (summed[i] / nodes[i].mass )*timestep)

def saveAnimation(network : Network, 
                  framerate : int, 
                  threshold : float = 0.01, 
                  filename : str = "network.gif", 
                  damping : float = 0.95,
                  framelimit : int = None):
  
  network.setMasses()
  
  locations = []
  velocities = []
  edges = []

  # Generates the lists used for frame rendering and the animation length criterion
  iterator : int = 0
  while iterator in range(20) or network.getMaxVelocity() > threshold:
    iterator = iterator + 1 
    print("\r",flush=True,end="")
    print(iterator, "frames",end="")
    updateNodes(network.nodes, 1 / framerate, damping)
    locations.append(network.getPositions())
    velocities.append(network.getVelocities())
    edges.append(network.getLinePairs())
  
  if framelimit is not None:
    locations  = locations[-framelimit:]
    velocities = velocities[-framelimit:]
    edges      = edges[-framelimit:]
  
  print("")

  locations = np.array(locations)
  velocities = np.array(velocities)
  edges = np.array(edges)

  # This scales the bounds so you can see the equilibrium state well,
  # but the really big behavior doesn't play too much of a role
  reverseFrames = -np.min([len(locations),150])
  print("Scaling bounds for for ", -reverseFrames, " frames")

  xmin = locations[reverseFrames:,:,0].min()
  xmin  = xmin - 0.1 * np.abs(xmin)
  xmax = locations[reverseFrames:,:,0].max()
  xmax  = xmax + 0.1 * np.abs(xmax)
  ymin = locations[reverseFrames:,:,1].min()
  ymin  = ymin - 0.1 * np.abs(ymin)
  ymax = locations[reverseFrames:,:,1].max()
  ymax  = ymax + 0.1 * np.abs(ymax)

  fig, ax = plt.subplots()
  ax.set_axis_off()
  ax.set_xlim([xmin,xmax])
  ax.set_ylim([ymin,ymax])

  lines = LineCollection(edges[0])
  ax.add_collection(lines)
  points = ax.scatter(locations[0,:,0],locations[0,:,1],c='black')


  def animate(i):
    lines.set_segments(edges[i])
    points.set_offsets(locations[i])
    return (points,lines)

  anim = animation.FuncAnimation(fig, animate, repeat=False, frames=len(locations), interval= 1000 / framerate, blit = True,)
  
  print("Saving ", len(locations), " frames...", end = "\r" , flush = True)
  
  # This function takes OBSCENELY long. Talk to the people at matplotlib about it though, not me...
  writer = animation.PillowWriter(fps= framerate ,bitrate=1200)
  anim.save(filename, writer=writer)
  
  print("Saved.                    ")

##################################################
# Demos ------------------------------------------ 
##################################################



def randomDemo(nodes : int = 7, edges: int = 12, chargeRange : float = 1.0, framelimit : int = None):
  # Generates a random assortment of nodes and edges, with node coordinates in (-5,5) x (-5,5)
  # you can also pick charge range if you wanted to...
  # also could change the framelimit
  
  net = Network()

  for i in range(nodes):
    node = net.addRandomNode(chargeRange = chargeRange)
  
  for i in range(edges):
    net.addRandomEdge()

  saveAnimation(net,30, threshold = .1, damping = 0.95,framelimit = framelimit)

# This guy *should* resolve itself into a "square" coming off one side of a pentagon
def squarePentagonDemo():

  net = Network()
  
  node1 = net.addNode(Node([0,2]))
  node2 = net.addNode(Node([-1,1]))
  node3 = net.addNode(Node([2,2]))
  node4 = net.addNode(Node([-1,0]))
  node5 = net.addNode(Node([2,1]))
  node6 = net.addNode(Node([3,1]))
  node7 = net.addNode(Node([1,3]))
  
  # Square and pentagon for 7 nodes
  net.addEdges([Edge(node1,node2),
                Edge(node2,node3),
                Edge(node3,node4),
                Edge(node4,node5),
                Edge(node5,node1),
                Edge(node5,node6),
                Edge(node6,node7),
                Edge(node7,node1)
                ])

  saveAnimation(net,30, threshold = .1)
  
randomDemo(nodes = 10, edges = 40, chargeRange = 20)