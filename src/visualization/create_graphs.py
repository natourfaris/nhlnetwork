import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

subgraph = nx.Graph()

subgraph_players = ['Sidney Crosby','Phil Kessel','Dion Phaneuf','Erik Karlsson']
game_names = ['2016020379a','2016020379h']

subgraph.add_nodes_from(subgraph_players,bipartite='players')
subgraph.add_nodes_from(game_names,bipartite='games')

subgraph.add_edges_from([('Sidney Crosby','2016020379h'),('Phil Kessel','2016020379h'),
                     ('Dion Phaneuf','2016020379a'),('Erik Karlsson','2016020379a')])

proj_graph = nx.algorithms.bipartite.projection.projected_graph(subgraph,subgraph_players)

figure = plt.figure(figsize=(10,6))
ax = plt.subplot(111)
top = nx.drawing.layout.bipartite_layout(subgraph,subgraph_players)
top = {k:(np.array([0.75,v[1]]) if k in subgraph_players else v) for k,v in top.items()}
nx.draw(subgraph,with_labels=True,pos=top)
plt.savefig('../../figures/bipartite.png')
plt.close()

figure = plt.figure(figsize=(10,6))
ax = plt.subplot(111)
nx.draw(proj_graph,pos={'Sidney Crosby':np.array([1.25,0.25]),
	'Phil Kessel':np.array([1.5,0.25]),
	'Dion Phaneuf':np.array([1.25,1.25]),
	'Erik Karlsson':np.array([1.5,1.25])},with_labels=True)
plt.savefig('../../figures/bipartite2.png')
plt.close()