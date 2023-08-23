import numpy as np
import math
import networkx as nx
from helpers import assign_fitness
import matplotlib.pyplot as plt
from helpers import draw_graph
import random

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

genY_percent = 0.5
genY_split = 0.7, 0.3
genZ_percent = 0.5

edges = []
curr_net_size = 0

def power_law_graph(_V, _n_0, _m_0 = 1, apply_fitness = True):
    global V, n_0, m_0, g_state, curr_net_size
    V, n_0, m_0 = _V, _n_0, _m_0
    
    init_gens()
    init_graph_state(apply_fitness)
    
    create_net_x()
    create_net_y()
    create_net_z()
    
    return g_state[d_index][0:curr_net_size], edges


def init_gens():
    global V, n_0, genX, genY, genZ
    
    genX = np.arange(n_0)
    last_index = n_0 + math.ceil(genY_percent * (V - n_0))
    genY = np.array(list(range(n_0, last_index)))
    genZ = np.array(list(range(last_index, V)))
    
    # print(f"GenX: {genX}, len = { len(genX) }")
    # print(f"GenY: {genY}, len = { len(genY) }")
    # print(f"GenZ: {genZ}, len = { len(genZ) }")
    
    
def patch_g_state(start = 0, end = curr_net_size):
    global g_state
    
    degree_times_fitness = g_state[d_index][start:end] * g_state[f_index][start:end]
    total_degree_times_fitness = sum(degree_times_fitness)
    g_state[p_index][start:end] = degree_times_fitness / total_degree_times_fitness
        
        
def init_graph_state(af = True):
    global V, n_0, g_state
    
    g_state = np.zeros((3, V))
    g_state[f_index] = assign_fitness(V, n_0) if af else np.ones(V)
    
    
def create_net_x():
    # print("Building Network X...")
    
    global g_state, edges, curr_net_size
    curr_net_size = n_0
    
    for src in range(0, n_0):
        for dst in range(src + 1, n_0):
            edges.append((src, dst, random.randint(1, 10)))
            g_state[d_index][src] += 1
            g_state[d_index][dst] += 1
            
    # draw_graph(edges=edges)
    
def create_net_y():
    # print("Building Network Y...")
    
    global genY, g_state, edges, curr_net_size
    
    part_2 = math.floor(genY_split[0] * len(genY))
    
    for i, node in enumerate(genY):
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
        
        extend_network(node, gen, weights)
        
        
def create_net_z():
    # print("Building Network Z")
    
    global genY, g_state, edges, curr_net_size
    
    start_i, end_i = (0, curr_net_size)
    
    for i, node in enumerate(genZ):
        patch_g_state(start_i, end_i)
        
        weights = g_state[p_index][start_i:end_i]
        
        gen = list(range(start_i, end_i))
        
        extend_network(node, gen, weights)
        
        
def extend_network(node, gen, weights):
    global curr_net_size, g_state, edges
    
    # print(f'gen: {len(gen)}')
    # print(f'weights: {len(weights)}')
    gen = gen[0:len(weights)]
    snodes = np.random.choice(gen, p=weights, size=m_0, replace=False)
        
    for snode in snodes:
        g_state[d_index][snode] += 1
        g_state[d_index][node] += 1
        
        edges.append((snode, node, random.randint(1, 10)))
        
    curr_net_size += len(snodes) # update graph size