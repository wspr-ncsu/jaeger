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
    fitness[0:n_0] = f
    f = decrement(f, 100)
    
    # Divide the new nodes into f groups, assign f and decrease f when group changes
    num_of_groups = 10
    group_size = (V - n_0) // num_of_groups
    start_index = n_0
    
    for group in range(num_of_groups):
        end_index = start_index + group_size
        for i in range(start_index, end_index):
            fitness[i] = f
        start_index = end_index
        
        f = decrement(f, 10)

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

def custom_power_law_graph(V, n_0, m_0 = 1, apply_fitness = True):
    edges = []
    curr_size = n_0
    # Setup
    num_of_gens = 5
    population_per_gen = math.ceil((V - n_0) / (num_of_gens - 1))
    generations = np.full((num_of_gens, population_per_gen), -1)
    
    # print(f"Population per generation: {population_per_gen}")
    # print(f"Dimensions of generation: {generations.shape}")
    
    # return
    
    # add edges in initial graph
    for src in range(0, n_0):
        for dst in range(src + 1, n_0):
            edges.append((src, dst))
    
    # fill generations with populations
    last_node_in_prev_gen = -1
    
    for gen in range(0, num_of_gens):
        if gen == 0:
            generations[gen][0:n_0] = np.array(list(range(0, n_0)))
            last_node_in_prev_gen = generations[gen][n_0 - 1]
        else:
            first_node_in_this_generation = last_node_in_prev_gen + 1
            members = np.array(list(range(first_node_in_this_generation, population_per_gen + first_node_in_this_generation)))
            generations[gen] = members
            last_node_in_prev_gen = generations[gen][-1]
            
    generations[num_of_gens - 1][-1] = -1
    
    # print(generations)
    
    graph = np.zeros((3, V))
    f_index, d_index, p_index = 0, 1, 2
    
    # assign fitness level to nodes
    graph[f_index] = assign_fitness(V, n_0) if apply_fitness else np.ones(V)
    
    # Create an initial clique by assigning degrees
    graph[d_index][0:curr_size] = n_0 - 1
    
    # fn to calculate probabilities of the current graph
    def calc_probs():
        degree_times_fitness = graph[d_index][0:curr_size] * graph[f_index][0:curr_size]
        total_degree_times_fitness = sum(degree_times_fitness)
        graph[p_index][0:curr_size] = degree_times_fitness / total_degree_times_fitness
    
    cascade_break = False
    
    for gen in range(1, num_of_gens): # skip initial generation
        # print(f"Outer Generation: {gen}")
        for node in generations[gen]:
            if node == -1:
                cascade_break = True
                break
            
            calc_probs()
            
            # candidate nodes to select = nodes in initial graph + nodes from previous generations
            candidates = np.array(list(range(0, n_0))) # initial graph
            
            # include nodes from prev generations not including 1st generation, i.e gen 0
            for curr in range(1, gen + 1):
                # print(f"Prev GEN: {curr}")
                num_nodes_to_select = 5 # n_0 - curr
                
                # get first and last members of the current generation
                first_member = generations[curr][0]
                last_member = generations[curr][-1] if generations[curr][-1] != -1 else generations[curr][-2]
                
                # get the weights of the members of current generation
                weights = graph[p_index][first_member : last_member + 1] + 1
                weights = weights / sum(weights)
                
                # print(f"first member: {first_member}")
                # print(f"last member: {last_member}")
                # print(f"Gen: {generations[curr]}")
                # print(f"Weights of gen {curr}")
                # print(weights)
                
                gens = generations[curr][0:len(weights)]
                
                # print(f"Gens to select from: {len(gens)}")
                
                selected_nodes_in_gen = np.random.choice(gens, p=weights, size=num_nodes_to_select, replace=False)
                # print(f"selected nodes in gen {curr}: {selected_nodes_in_gen}")
                candidates = np.concatenate((candidates, selected_nodes_in_gen))
                
            # print("Candidates")
            # print(candidates)
            
            weights = []
            
            for candidate in candidates:
                weights.append(graph[p_index][candidate])
            
            # print("Candiate Weights:")
            # print(weights)
            
            selected_nodes = np.random.choice(candidates, p=weights, size=m_0, replace=False)
            
            # print("Selected Nodes")
            # print(selected_nodes)
            
            for selected_node in selected_nodes:
                graph[d_index][selected_node] += 1
                graph[d_index][node] += 1
                
                edges.append((selected_node, node))
        
        if cascade_break is True:
            break
        
    return graph[d_index], edges

def distribution(degrees):
    x, freqs = np.unique(degrees, return_counts=True)
    
    bounds = {
        'heavy hitters (500+)': (500, None),
        '201 - 499': (201, 499),
        '101 - 200': (101, 200),
        '51 - 100': (51, 100),
        '21 - 50': (21, 50),
        '11 - 20': (11, 20),
        '4 - 10': (4, 10),
        '2 - 3': (2, 3),
    }
    
    data = {}
    
    # for key in bounds.keys():
    #     data[key] = 0
    
    for i in range(0, len(x)):
        degree = x[i]
        # print(f"Checking degree: {degree}, freq: {freqs[i]}")
        
        for key in bounds.keys():
            bound = bounds[key]
            if bound[1] is None:
                if degree >= bound[0]:
                    data[key] = data[key] + freqs[i] if key in data.keys() else freqs[i]
            else:
                if degree >= bound[0] and degree <= bound[1]:
                    data[key] = data[key] + freqs[i] if key in data.keys() else freqs[i]
            
    
    total_freqs = sum(freqs)
    data_total = sum(data.values())
    
    # print(f"Total freqs: {total_freqs}")
    # print(f"Total data: {data_total}")
    
    # for key in data.keys():
    #     print(f"{key}: {data[key]}")
        
    return data, total_freqs

def plot_degree_distribution(degrees, title = "Degree distribution"):
    x, freqs = np.unique(degrees, return_counts=True)
    
    data = {}
    # total_freq = sum(freqs)
    for i in range(0, len(x)):
        data[int(x[i])] = freqs[i]
        
    print(data)
    
    # Normalize the counts
    sum_freq = sum(freqs)
    y = [freq / sum_freq for freq in freqs]
    
    # print(sum(y))
    
    # Plot the degree distribution as a line graph
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, y, linestyle='-', color='b', linewidth=1)

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
    
def draw_graph(edges):
    G = nx.Graph()
    G.add_weighted_edges_from(edges)

    # Draw the graph using Matplotlib
    nx.draw(G, with_labels=True, node_color='lightblue', font_weight='bold')
    plt.show()