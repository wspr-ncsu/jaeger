import networkx as nx
from typing import List
import matplotlib.pyplot as plt
from jager.helpers import Logger as logger
from colorama import Fore


G = None
DEV = True
routes = []
in_degs = {}
out_degs = {}

def init(msgs: List[str], dev = True):
    global G, in_degs, out_degs, routes, DEV
    DEV = dev
    routes = list(set(msgs))
    G = create_graph(routes)
    for node, in_deg in G.in_degree():
        in_degs[node] = in_deg
    for node, out_deg in G.out_degree():
        out_degs[node] = out_deg
        

def create_graph(routes: List[str]):
    G = nx.MultiDiGraph()
    
    for route in routes:
        if route == None:
            continue
        
        prev, curr, next = route.split('|')
        
        if prev == 'None':
            G.add_edge(curr, next)
            continue
        
        if next == 'None':
            G.add_edge(prev, curr)
            continue
        
        G.add_edge(prev, curr)
        G.add_edge(curr, next)
    return G

def analyze():
    DEV and print("\n")
    origins = check_origin_invariant()
    terminatings = check_terminal_invariant()
    transits = check_transit_invariant()
    is_connected = check_connectivity()
    
    if is_connected:
        for origin in origins:
            for terminal in terminatings:
                draw_paths(origin=origin, terminal=terminal)
                
    DEV and print('\nDecrypted records', sub=False)
    for msg in routes:
        if msg not in [None, 'None']:
            DEV and print(msg.replace('None|', '').replace('|None', '').replace('|', ' -> '), prefix='*')
    
        
def draw_paths(origin, terminal):
    path = nx.shortest_path(G, origin, terminal)
    DEV and print("Possible paths from {} to {}: {}{}".format(origin, terminal, Fore.YELLOW, " -> ".join(path)))

def check_connectivity():
    DEV and print('Checking connectivity (Can all records be linked)', sub=False)
    is_connected = nx.is_weakly_connected(G)
    
    if is_connected:
        DEV and logger.success('YES')
    else:
        DEV and print('NO')
        
    return is_connected
    
def check_origin_invariant():
    DEV and print('Checking origin invariant', sub=False)
    
    # get all nodes with in-degree 0 and out-degree > 0
    origins = []
    for node in G.nodes():
        if in_degs[node] == 0 and out_degs[node] > 0:
            origins.append(node)
    
    if len(origins) == 1:
        DEV and logger.success(f'{display_nodes(origins)}')
    elif len(origins) > 1:
        # from these nodes, get the ones with out-degree 2
        yes, no = get_nodes_from(origins, having_in_deg=0, having_out_deg=2)
        
        if no:
            DEV and print('The following nodes claim to be originators but no transit carrier attested to their claim:')
            DEV and print(display_nodes(no))
        
        if yes:
            DEV and print('The following nodes claim to be originators and at least 1 transit carrier attested to their claim:')
            DEV and logger.success(display_nodes(yes))
        
        origins = yes
    else:
        DEV and print('NO: None found')
        
    return origins
        
def check_terminal_invariant():
    DEV and print('Checking Terminal invariant', sub=False)
    
    # get all nodes with in-degree > 0 and out-degree = 0
    terminals = []
    for node in G.nodes():
        if in_degs[node] > 0 and out_degs[node] == 0:
            terminals.append(node)
    
    if len(terminals) == 1:
        DEV and logger.success(f'{display_nodes(terminals)}')
    elif len(terminals) > 1:
        # from these nodes, get the ones with in-degree 2
        yes, no = get_nodes_from(terminals, having_in_deg=2, having_out_deg=0)
        
        if no:
            DEV and print('The following carriers claim to be terminals but no transit carrier attested to their claim:')
            DEV and print(display_nodes(no))
        
        if yes:
            DEV and print('The following carriers claim to be terminals and at least 1 transit carrier attested to their claim:')
            DEV and logger.success(display_nodes(yes))
            
        terminals = yes
    else:
        DEV and print('NO: None found')
        
    return terminals

def check_transit_invariant():
    DEV and print('Checking transit invariant (All other nodes must have in-degree, out-degree either 1 or 2)', sub=False)
    transits = []
    
    for node in G.nodes():
        if (in_degs[node] >= 1 and in_degs[node] <= 2) and (out_degs[node] >= 1 and out_degs[node] <= 2):
            transits.append(node)
    
    if len(transits):
        DEV and logger.success(display_nodes(transits))
    else:
        DEV and print('NO: No transit carriers found')
        
    return transits

def get_nodes_with_degrees(in_deg=None, out_deg=None):
    nodes = []
    
    if in_deg == None and out_deg == None:
        return nodes
    
    for node in G.nodes():
        if in_degs[node] == in_deg and out_degs[node] == out_deg:
            nodes.append(node)
            
    return nodes

def get_nodes_from(nodes, having_in_deg, having_out_deg):
    yes = []
    nos = []
    for node in nodes:
        if in_degs[node] == having_in_deg and out_degs[node] == having_out_deg:
            yes.append(node)
        else:
            nos.append(node)
            
    return yes, nos

def display_nodes(nodes):
    return ", ".join(nodes)

def get_subgraphs():
    return list(nx.weakly_connected_components(G))