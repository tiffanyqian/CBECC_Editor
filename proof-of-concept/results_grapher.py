import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import re

input_filename = input(r"Enter CSV File Name/Path: ")
if len(input_filename) == 0:
    exit("Enter a valid file.")

results_df = pd.read_csv(input_filename,header=None).dropna(axis=1)
results_df = results_df.iloc[1::2,:].reset_index(drop=True)
results_df = pd.concat([results_df.iloc[:,0],results_df.iloc[:,5::2]],axis=1)

G = nx.DiGraph(directed=True)

for result in results_df.values:
    casename = result[0]
    node_list = re.findall(r"(?:Case.*?(\d+))+",casename)

    G.add_node(int(node_list[0]))
    for n in node_list[1:]:
        G.add_edge(int(n), int(node_list[0]), weight=0.25)

plt.plot(1)
pos = nx.bfs_layout(G,0)
nx.draw_networkx_nodes(G, pos)
nx.draw_networkx_labels(G, pos)
nx.draw_networkx_edges(G, pos, arrows=True)

plt.show()
