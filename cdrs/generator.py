import random
import secrets
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime
import requests
from phone_network import create_network

CONTRIBUTION_URL = 'http://127.0.0.1:5000/contribute'

subscribers = []
user_network = None
phone_network = None
market_shares = None
same_network_call = 0
cross_network_call = 0

def create_user_network():
    global user_network
    user_network = nx.barabasi_albert_graph(len(subscribers), 2)


def assign_subscribers_by_market_share(carrier, market_share, num_subs):
    global subscribers
    subscribers_count = round(num_subs * market_share)
    
    for i in range(subscribers_count):
        subscribers.append(make_subscriber(carrier))
        
        
def make_subscriber(carrier):
    npa = random.randint(200, 999)
    nxx = random.randint(100, 999)
    num = random.randint(1000, 9999)
    
    return f"{carrier}:{npa}-{nxx}-{num}"


def shuffle_subscribers():
    global subscribers
    # Fisher-Yates shuffle algorithm
    for i in reversed(range(1, len(subscribers))):
        j = secrets.randbelow(i + 1)
        subscribers[i], subscribers[j] = subscribers[j], subscribers[i]
            
            
def create_phone_network(num_carriers, n_0, m_0):
    global phone_network
    
    graph = nx.Graph()
    degrees, edges = create_network(num_carriers, n_0, m_0, apply_fitness=True)
    graph.add_weighted_edges_from(edges)
    
    phone_network = graph

def generate_market_shares():
    global market_shares
    
    total_degrees = 2 * len(phone_network.edges)
    num_carriers = len(phone_network.nodes)
    shares = np.zeros(num_carriers)
    
    for i in range(num_carriers):
        shares[i] = phone_network.degree[i] / total_degrees
        
    market_shares = shares

def simulate_call(src, dst):
    global same_network_call, cross_network_call
    source, src_tn = src.split(':')
    target, dst_tn = dst.split(':')
    
    source, target = int(source), int(target)
    
    if source == target:
        same_network_call += 1
        return
    else:
        cross_network_call += 1
    
    
    if source not in phone_network or target not in phone_network:
        return
    
    # Find the call path
    call_path = nx.shortest_path(phone_network, source=source, target=target, weight='weight')
    
    # Map integer based indices to real carrier pointers 
    call_path = list(call_path)
    
    for (index, carrier) in enumerate(call_path):
        prev = next = None
        
        if index > 0: 
            prev = call_path[index - 1]
            
        if index < len(call_path) - 1:
            next = call_path[index + 1]
            
        ts = round(datetime.now().timestamp())
        
        # create CDR tupple
        cdr = (src_tn, dst_tn, ts, prev, carrier, next)
        
        # Simulate record submission to traceback server
        contribute(cdr)
            
def contribute(cdr):
    print(f'Saving {cdr}')
    

def draw_graph(G):
    nx.draw(G, with_labels=True, node_color='lightblue', font_weight='bold')
    plt.show()
    
def to_json(data):
    return json.dumps(data, indent=4)
    
def simulate():
    for edge in user_network.edges:
        src = subscribers[edge[0]]
        dst = subscribers[edge[1]]
        print(edge)
        try:
            simulate_call(src, dst)
        except IndexError as err:
            print(err)
                
def run(num_subs, num_carriers):
    create_phone_network(num_carriers, 5, 2)
    generate_market_shares()
    
    for carrier in phone_network.nodes:
        assign_subscribers_by_market_share(carrier, market_shares[carrier], num_subs)
        
    create_user_network()
    
    shuffle_subscribers()
        
    print(f'total subs: {len(subscribers)}')
    
    simulate()
 
def get_input(prompt, default=None):
    response = input(prompt)
    return response if response else default
    
if __name__ == '__main__':
    num_carriers = int(get_input(f'Number of carriers (default is 50): ', 50))
    num_subs = int(get_input(f'Number of subscribers (default is 1000): ', 1000))
    
    run(num_subs=num_subs, num_carriers=num_carriers)