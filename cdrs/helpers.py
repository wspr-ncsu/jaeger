import numpy as np
import networkx as nx
import random
import math
import powerlaw
import matplotlib.pyplot as plt

def decrement(f, by = 1):
    if f > by:
        return f - by
    return f

def assign_fitness(V, n_0):
    f = V // n_0
    
    fitness = np.zeros(V)
    
    # Assign high fitness to initial nodes
    fitness[0:n_0] = n_0
    f = decrement(f)
    
    # Divide the new nodes into f groups, assign f and decrease f when group changes
    group_size = (V - n_0) // f
    
    for i in range(n_0, V):
        fitness[i] = f
        
        if (i - n_0 + 1) % group_size == 0 and f > 1:
            f = decrement(f)

    return fitness

def bianconi_barabasi(V, n_0, m_0 = 1, apply_fitness = True):
    # tracks the size of initial graph
    curr_size = n_0
    
    # Create a 2D graph with 3 rows and V columns each
    # row index 0 = fitness, row index 1 = degrees and row index 2 = probabilities
    graph = np.zeros((3, V))
    f_index, d_index, p_index = 0, 1, 2
    
    # assign fitness level to nodes
    graph[f_index] = assign_fitness(V, n_0) if apply_fitness else np.ones(V)
    
    # print(graph[f_index])
    
    # Create an initial clique by assigning degrees
    graph[d_index][0:curr_size] = n_0 - 1
    
    # fn to calculate probabilities of the current graph
    def calc_probs():
        degree_times_fitness = graph[d_index][0:curr_size] * graph[f_index][0:curr_size]
        total_degree_times_fitness = sum(degree_times_fitness)
        graph[p_index][0:curr_size] = degree_times_fitness / total_degree_times_fitness
    
    # for the remaining nodes, n_0 to V
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
    
    return graph[d_index]   


def plot_degree_distribution(degrees, title = "Degree distribution"):
    x, freqs = np.unique(degrees, return_counts=True)
    
    data = {}
    # total_freq = sum(freqs)
    for i in range(0, len(x)):
        data['deg ' + str(int(x[i]))] = freqs[i]
        
    print(data)
    
    # Normalize the counts
    sum_freq = sum(freqs)
    y = [freq / sum_freq for freq in freqs]
    
    # print(sum(y))
    
    # Plot the degree distribution as a line graph
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x, y, linestyle='-', color='b', linewidth=1)

    ax.set_title(title)
    ax.set_xlabel("Degrees, x")
    ax.set_ylabel("Probabilities, P(x)")

    plt.show()

def show_goodness_of_fit(degrees):
    results = powerlaw.Fit(degrees)

    print(f"alpha: {results.power_law.alpha}")
    print(f"Xmin: {results.power_law.xmin}")
    
    R, p = results.distribution_compare('power_law', 'lognormal')
    
    print(f"Log-likelihood ratio (R): {R}")
    print(f"p-value: {p}")