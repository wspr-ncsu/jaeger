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
from uuid import uuid4
from . import database
from .phone_network import create_network
from .helpers import timed
import argparse
from . import subscribers_network

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

def create_user_network(subnets):
    num_subs = len(subscribers)
    robocallers = 0
    subscribers_network.create_subscribers_network((num_subs, subnets), robocallers)


def assign_subscribers_by_market_share(carrier, market_share, num_subs):
    global subscribers
    subscribers_count = round(num_subs * market_share)
    
    for i in range(subscribers_count):
        subscribers.append(make_subscriber(carrier))
        
        
def make_subscriber(carrier):
    npa = random.randint(200, 999)
    nxx = random.randint(100, 999)
    num = str(random.randint(0, 9999)).zfill(4)
    
    return carrier, f"{carrier}:{npa}-{nxx}-{num}"


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
    
    cdrs = []
    
    for (index, carrier) in enumerate(call_path):
        prev = next = None
        
        if index > 0: 
            prev = call_path[index - 1]
            
        if index < len(call_path) - 1:
            next = call_path[index + 1]
            
        ts = round(datetime.now().timestamp())
        
        # create CDR tupple
        cdr = [src_tn, dst_tn, str(ts), str(prev), str(carrier), str(next)]
        cdrs.append(cdr)
        
    return cdrs


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
    
def init_user_network(num_subs, subnets):
    for carrier in phone_network.nodes:
        assign_subscribers_by_market_share(carrier, market_shares[carrier], num_subs)
    timed(shuffle_subscribers)()
    timed(save_subscribers)()
    timed(create_user_network)(subnets)
 
def fresh_start(num_carriers):
    init_phone_network(num_carriers)
    set_cache()
    
def save_subscribers():
    data = []
    batch = 0
    
    for id, (carrier, phone) in enumerate(subscribers):
        data.append([str(id), str(phone), str(carrier)])
        if id > 0 and id % 10000 == 0:
            batch += 1
            print(f'-> Saving Batch {batch} subscribers. Total saved: {id}')
            database.save_subscribers(data)
            data = []      
            
    if len(data) > 0:
        print(f'-> Saving Batch {batch + 1} subscribers. Total saved: {id}')
        database.save_subscribers(data)
