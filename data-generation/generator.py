import random
import secrets
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime
from models.phone_network import create_network
import pickle
import os
import argparse

CONTRIBUTION_URL = 'http://127.0.0.1:5000/contribute'

subscribers = []
cache_file = 'cache.pkl'
user_network = None
phone_network = None
shortest_paths = None
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
    
    # Map integer based indices to real carrier pointers 
    call_path = get_call_path(source, target)
    
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


def all_pairs_johnson():
    global shortest_paths
    shortest_paths = nx.johnson(phone_network, weight='weight')
    
    
def get_call_path(source, target):
    return shortest_paths[source][target]
    
def contribute(cdr):
    # print(f'Saving {cdr}')
    pass
    

def draw_graph(G):
    nx.draw(G, with_labels=True, node_color='lightblue', font_weight='bold')
    plt.show()
    
def to_json(data):
    return json.dumps(data, indent=4)
    
def simulate():
    total = len(user_network.edges)
    start_time = datetime.now()
    
    shared_count = 90000
    
    for i, edge in enumerate(user_network.edges):
        src = subscribers[edge[0]]
        dst = subscribers[edge[1]]
        # print(f'[{i+1}/{total}]:: {src} -> {dst}')
        
        try:
            simulate_call(src, dst)
        except IndexError as err:
            print(err)
        
        if (i + 1) % shared_count == 0:
            elapsed = get_elapsed_time(start_time)
            print(f'[{i+1}/{total}]:: Elapsed time: {elapsed} seconds')
            start_time = datetime.now()

def set_cache():
    data = (phone_network, shortest_paths, market_shares)
    with open(cache_file, 'wb') as file:
        pickle.dump(data, file)

def load_cache(num_carriers):
    global phone_network, shortest_paths, market_shares
    
    if not os.path.exists(cache_file):
        return False
    
    print('Loading phone network metadata from cache...')
    
    with open(cache_file, 'rb') as file:
        pn, sp, ms = pickle.load(file)
        phone_network = pn
        shortest_paths = sp
        market_shares = ms
    
    if len(phone_network.nodes) != num_carriers:
        return False
    
    return phone_network is not None and shortest_paths is not None and market_shares is not None
    
    
def init_phone_network(num_carriers, use_cache=False):
    timed(create_phone_network)(num_carriers, 5, 2)
    timed(generate_market_shares)()
    timed(all_pairs_johnson)()
    
    timed(set_cache)() if use_cache else None
    
def run(num_subs, num_carriers, use_cache=False):
    def runner():
        if use_cache:
            init_phone_network(num_carriers, use_cache=use_cache) if not timed(load_cache)(num_carriers) else None
        else:
            init_phone_network(num_carriers, use_cache=use_cache)
        
        for carrier in phone_network.nodes:
            assign_subscribers_by_market_share(carrier, market_shares[carrier], num_subs)
            
        timed(create_user_network)()
        
        timed(shuffle_subscribers)()
        
        simulate()
        
    timed(runner)()
 
def get_input(prompt, default=None):
    response = input(prompt)
    return response if response else default

def timed(func):
    def wrapped(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        print(f'{func.__name__} finished in {get_elapsed_time(start)} seconds')
        return result
    return wrapped

def get_elapsed_time(start):
    return round((datetime.now() - start).total_seconds(), 2)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate CDRs')
    parser.add_argument('-c', '--carriers', type=int, help='Number of carriers', default=2000)
    parser.add_argument('-s', '--subscribers', type=int, help='Number of subscribers', default=1000000)
    args = parser.parse_args()
    print(args)
    run(num_carriers=args.carriers, num_subs=args.subscribers)