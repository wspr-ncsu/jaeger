import numpy as np
import math
import networkx as nx
from helpers import assign_fitness
import matplotlib.pyplot as plt

# parameters
V = 7000
n_0 = 5
m_0 = 1

# 3 generations
genX = None
genY = None
genZ = None

f_index, d_index, p_index = 0, 1, 2
g_state = None

genY_percent = 0.6
genY_split = 0.7, 0.3
genZ_percent = 0.4

edges = []
curr_net_size = 0

def power_law_graph(_V, _n_0, _m_0 = 1, apply_fitness = True):
    global V, n_0, m_0, g_state, curr_net_size
    V, n_0, m_0 = _V, _n_0, _m_0
    
    init_gens()
    init_graph_state(apply_fitness)
    create_net_x()
    create_net_y()
    
    return g_state[d_index][0:curr_net_size], edges


def init_gens():
    global V, n_0, genX, genY, genZ
    
    genX = np.arange(n_0)
    last_index = n_0 + math.ceil(genY_percent * (V - n_0))
    genY = np.array(list(range(n_0, last_index)))
    genZ = np.array(list(range(last_index, V)))
    
    
def patch_g_state(start = 0, end = curr_net_size):
    global g_state
    
    d_x_f = g_state[d_index][start:end] * g_state[f_index][start:end]
    td_x_f = sum(d_x_f)
    g_state[p_index][start:end] = d_x_f / td_x_f
        
        
def init_graph_state(af = True):
    global V, n_0, g_state
    
    g_state = np.zeros((3, V))
    g_state[f_index] = assign_fitness(V, n_0) if af else np.ones(V)
    
    
def create_net_x():
    print("Building Network X...")
    
    global g_state, edges, curr_net_size
    curr_net_size = n_0
    
    G = nx.barabasi_albert_graph(n_0, 2)
    edges = list(G.edges())
    
    for node in G.nodes():
        g_state[d_index][node] = G.degree(node)
        
    print(f"GenX degrees: {g_state[d_index][0:n_0]}" )
    nx.draw(G, with_labels=True, node_color='lightblue', font_weight='bold')
    plt.show()
    
def create_net_y():
    print("Building Network Y...")
    
    global genY, g_state, edges, curr_net_size
    
    part_2 = math.floor(genY_split[0] * len(genY))
    
    # print(f"start_of_part_2: {genY[part_2]}")
    
    for i, node_in_geny in enumerate(genY):
        if i < part_2:
            start_i = 0
            end_i = n_0
            gen = genX
        else: 
            start_i = genY[0]
            ei = part_2 - 1
            
            end_i = genY[ei]
            gen = genY[0:ei]
        
        patch_g_state(start_i, end_i)
        
        weights = g_state[p_index][start_i:end_i]
        
        # print(f"Weights: {weights}, sum: {sum(weights)}")
        # print(f"gen: {gen}")
        snodes = np.random.choice(gen, p=weights, size=m_0, replace=False)
        
        # print(f"selected Nodes for {node_in_geny}: {snodes}")
        
        for snode in snodes:
            g_state[d_index][snode] += 1
            g_state[d_index][node_in_geny] += 1
            
            edges.append((snode, node_in_geny))
            
        curr_net_size += len(snodes) # update graph size
        
        
def create_net_z():
    print("Building Network Z")
    
    global genY, g_state, edges, curr_net_size