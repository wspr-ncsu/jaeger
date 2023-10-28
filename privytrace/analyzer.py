import networkx as nx
from typing import List
import matplotlib.pyplot as plt
from privytrace.helpers import Logger as logger


G = None
in_degs = {}
out_degs = {}
origin = None
terminating = None
transits = []

def init(routes: List[str]):
    global G, in_degs, out_degs
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
    """
        1. Graph must be strongly connected
        2. Exactly 1 node with in-degree 0 and out-degree 2 (origin)
        3. Exactly 1 node with in-degree 2 and out-degree 0 (terminating)
        4. All other nodes must have in-degree 2 and out-degree 2
    """
    print("\n")
    check_connectivity()
    origins = check_origin_invariant()
    terminatings = check_terminating_invariant()
    transits = check_transit_invariant()

def check_connectivity():
    logger.default('Checking connectivity (Can all records be linked)', sub=False)
    is_connected = nx.is_weakly_connected(G)
    
    if is_connected:
        logger.success('YES')
    else:
        logger.error('NO')
        
    return is_connected
    
def check_origin_invariant():
    logger.default('Checking origin invariant', sub=False)
    
    # get all nodes with in-degree 0 and out-degree > 0
    origins = []
    for node in G.nodes():
        if in_degs[node] == 0 and out_degs[node] > 0:
            origins.append(node)
    
    if len(origins) == 1:
        logger.success(f'YES: {display_nodes(origins)}')
    elif len(origins) > 1:
        logger.warn('More than 1 origins found')
        # from these nodes, get the ones with out-degree 2
        yes, no = get_nodes_from(origins, having_in_deg=0, having_out_deg=2)
        
        if no:
            logger.warn('The following nodes claim to be originators but no transit carrier attested to their claim:')
            logger.default(display_nodes(no))
        
        if yes:
            logger.warn('The following nodes claim to be originators but and at least 1 transit carrier attested to their claim:')
            logger.success(f'{display_nodes(yes)} is possibly the origin')
    else:
        logger.error('NO: None found')
        
    return origins
        
def check_terminating_invariant():
    logger.default('Checking terminating invariant (Exactly 1 node with in-degree 2 and out-degree 0)', sub=False)
    terminatings = get_nodes_with_degrees(in_deg=2, out_deg=0)
    
    if len(terminatings) == 1:
        logger.success('YES')
    else:
        logger.error('NO')
        
    return terminatings

def check_transit_invariant():
    logger.default('Checking transit invariant (All other nodes must have in-degree 2 and out-degree 2)', sub=False)
    transits = get_nodes_with_degrees(in_deg=2, out_deg=2)
    
    if len(transits) == len(G.nodes()) - 2:
        logger.success('YES')
    else:
        logger.error('NO')
        
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