import sys
import os
import json
import pickle
import random
import secrets
import numpy as np
import networkx as nx
from datetime import datetime
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import pathlib
import models.database as database
from models.phone_network import create_network
from models.helpers import timed, get_elapsed_time

load_dotenv()

CONTRIBUTION_URL = 'http://127.0.0.1:5000/contribute'

subscribers = []
user_network = None
phone_network = None
shortest_paths = None
market_shares = None
same_network_call = 0
cross_network_call = 0
cache_file = pathlib.Path.cwd().joinpath('cache.pkl')

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
    
    carrier = str(carrier).zfill(4)
    
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


def all_pairs_johnson():
    global shortest_paths
    shortest_paths = nx.johnson(phone_network, weight='weight')
    
    
def get_call_path(source, target):
    return shortest_paths[source][target]


def set_cache():
    data = (phone_network, shortest_paths, market_shares)
    with open(cache_file, 'wb') as file:
        pickle.dump(data, file)

def load_cache():
    global phone_network, shortest_paths, market_shares
    
    if not os.path.exists(cache_file):
        return False
    
    print('Loading phone network metadata from cache...')
    
    with open(cache_file, 'rb') as file:
        pn, sp, ms = pickle.load(file)
        phone_network = pn
        shortest_paths = sp
        market_shares = ms
    
    return phone_network is not None and shortest_paths is not None and market_shares is not None
    
    
def init_phone_network(num_carriers):
    timed(create_phone_network)(num_carriers, 5, 2)
    timed(generate_market_shares)()
    timed(all_pairs_johnson)()
    
def init_user_network(num_subs):
    for carrier in phone_network.nodes:
        assign_subscribers_by_market_share(carrier, market_shares[carrier], num_subs)
    timed(create_user_network)()
    timed(shuffle_subscribers)()
    
def save_user_network():
    total = len(user_network.edges)
    shared_count = 1000
    batch = []
    database.clear_user_network()
    
    for i, edge in enumerate(user_network.edges):
        src = subscribers[edge[0]]
        dst = subscribers[edge[1]]
        batch.append([i, src, dst])
        if len(batch) == shared_count or i == total - 1:
            database.save_user_network(batch)
            batch = []
 
def get_input(prompt, default=None):
    response = input(prompt)
    return response if response else default

def fresh_start():
    info("Generating new phone network...")
    num_carriers = int(get_input('Enter number of carriers: '))
    init_phone_network(num_carriers)
    set_cache()
    num_subs = int(get_input('Enter number of subscribers: '))
    init_user_network(num_subs=num_subs)
    save_user_network()
    
def resume():
    if cache_file.exists():
        info("Resuming from cache.pkl file")
        info("Delete the cache.pkl pickle file to start fresh.")
        
        if not load_cache():
            info("Cache file is invalid. Generating new phone network...")
            fresh_start()
    else:
        fresh_start()
        
def create_cdrs():
    pass

def info(what):
    print("-->", what)
    

if __name__ == '__main__':
    cmd = sys.argv[1] if 1 < len(sys.argv) else None
    if cmd == 'migrate':
        database.migrate()
    elif cmd == 'run':
        resume()
    else:
        print('Invalid command')
        sys.exit(1)
