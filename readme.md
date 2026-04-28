This is my first project in Python. It is effectively a physics simulation, motivated by network layout optimization.

Background:
The inspiration for this project came from drawing a very ugly flowchart and wondering if there was a way to make the layout more natural and less messy. I Googled it and just saw the phrase "charged particles and springs" and thought it was such a cool way to approach the problem. I sat down that weekend and did the math for the physics simulation. The following weekend, I started writing the program.

Functions:
Using the program is pretty simple, especially in an interactive environment/notebook
 1. NETWORKS
    You first need to initialize a Network class. This guy contains Nodes and Edges objects, a couple useful methods, and is necessary to save an animation.

 2. ADDING NODES AND EDGES
    Initializing Node and Edge objects is fairly simple. 

    Node classes take up to three arguments: position, charge, and velocity in the form
     Node(pos = list[float], charge = float, vel = list[float]) 
    with
     Node([x,y]) 
    defaulting charge = 1 and velocity = [0,0]
   
    ** Note that list inputs longer than 2 will be truncated to their first element
    
    Edges take two nodes and a spring constant in the form
     Edge(node1 = Node, node2 = Node, k = float)
    with
     Edge(node1,node2) 
    defaulting k = 1
      
    The best way to add nodes at specific points and edges between them is:
     ```python
     # Initialize network
     net = Network()


     # Use the addNode function
     node1 = net.addNode(Node([0,1]))
     node2 = net.addNode(Node([1,0]))

     # Use the addRandomNode(coordRange,chargeRange) to add a node at a random position and charge
     # coordRange is default (-5,5) and chargeRange is default exactly 1. If chargeRange ≠ 1, charge is picked from (0,chargeRange)
     node3 = net.addRandomNode()

     # Use the addEdge function for two nodes of choice
     net.addEdge(Edge(node1,node2))
     
     # Use the addRandomEdge() to add an edge between two nodes at random (doesn't repeat)
     net.addRandomEdge()


     # Or use addNodes/addEdges([nodes/edges]) to add a bunch at once

    ```

 3. SAVING ANIMATION
    Once you've got your network all set up, you can save the simulation with certain parameters using
     ```python
     saveAnimation(network : Network, 
                   framerate : int, 
                   threshold : float = 0.01, 
                   filename : str = "network.gif", 
                   damping : float = 0.95,
                   framelimit : int = None)
    ```
    where
     network    is your target network
     framerate  is the desired gif framerate
     threshold  determines what max node velocity must decrease to to stop the animation (default to 0.1)
     filename   is the output file name
     damping    is how much the node velocities are damped per frame (necessary to prevent permanent oscillations)
     framelimit is how many frames backward from the end should be rendered (for really long simulations)

    This will save the animation as a gif to your working directory

 4. DEMOS
    There are a couple demo functions included.
    You can run randomDemo() or squarePentagonDemo() and fiddle with the randomDemo parameters to generate a couple cool examples

That's about it! There are a couple bugs/oversights I would fix as you could probably break it pretty fast if you really wanted to. It's a personal project, though, so I'm not gonna stress it too bad. In the future I would definitely encapsulate the node updating and physics calculations a bit better, but oh well...