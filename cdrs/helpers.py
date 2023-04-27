import numpy as np
import networkx as nx
import random
import math
import matplotlib.pyplot as plt

def decrement(f, by = 1):
    if f > by:
        return f - by
    return f

def assign_fitness(V, n_0):
    f = V // n_0
    
    fitness = np.zeros(V)
    
    # Assign high fitness to initial nodes
    fitness[0:n_0] = f
    f = decrement(f)
    
    # Divide the new nodes into f groups, assign f and decrease f when group changes
    group_size = (V - n_0) // f
    
    for i in range(n_0, V):
        fitness[i] = f
        
        if (i - n_0 + 1) % group_size == 0 and f > 1:
            f = decrement(f)

    return fitness

def bianconi_barabasi(V, n_0, m_0 = 1, apply_fitness = True):
    curr_size = n_0
    
    # Create a 2D graph with 3 rows and V columns each
    # row index 0 = fitness, row index 1 = degrees and row index 2 = probabilities
    graph = np.zeros((3, V))
    f_index, d_index, p_index = 0, 1, 2
    
    graph[f_index] = assign_fitness(V, n_0) if apply_fitness else np.ones(V)
    
    # Create an initial clique and assign degrees
    graph[d_index][0:curr_size] = n_0 - 1
    
    def calc_probs():
        degree_times_fitness = graph[d_index][0:curr_size] * graph[f_index][0:curr_size]
        total_degree_times_fitness = sum(degree_times_fitness)
        graph[p_index][0:curr_size] = degree_times_fitness / total_degree_times_fitness
    
    for node in range(n_0, V):
        calc_probs()
        
        # select m_0 nodes from existing nodes
        nodes_in_current_graph = list(range(0, curr_size))
        weights = graph[p_index][0:curr_size]
        selected_nodes = np.random.choice(nodes_in_current_graph, p=weights, size=m_0, replace=False)
        
        for selected_node in selected_nodes:
            graph[d_index][selected_node] += 1
            graph[d_index][node] += 1
            
        curr_size += 1
        
        # print(f"====== Node {node} ======")
        # print("nodes in graph")
        # print(nodes_in_current_graph)
        # print('weights')
        # print(weights)
        # print("selected node")
        # print(selected_nodes)
    
    return graph[d_index]   


def plot_degree_distribution(degrees, title = "Degree distribution", log_log = False):
    x, freqs = np.unique(degrees, return_counts=True)
    
    # Normalize the counts
    sum_freq = sum(freqs)
    y = [freq / sum_freq for freq in freqs]
    
    # print(sum(y))
    
    # Plot the degree distribution as a line graph
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x, y, linestyle='-', color='b', linewidth=1)

    if log_log == True:
        x = [math.log(i) for i in x]
        y = [math.log(i) for i in y]

        slope, y_intercept = np.polyfit(x, y, 1)

        # Plot the line of best fit
        ax.plot(x, slope * x + y_intercept, color='red', linestyle='--', linewidth=2)
        print(f"Slope: {slope}, y-intercept: {y_intercept}")

    ax.set_title(title)
    ax.set_xlabel("Degrees, x")
    ax.set_ylabel("Probabilities, P(x)")

    plt.show()
