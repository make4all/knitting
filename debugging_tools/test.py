import networkx as nx
import matplotlib.pyplot as plt
g = nx.DiGraph()
g.add_edge(131,673,weight=673)
g.add_edge(131,201,weight=201)
g.add_edge(673,96,weight=96)
g.add_edge(201,96,weight=96)
print(nx.shortest_path(g,source=131,target=96, weight='weight'))