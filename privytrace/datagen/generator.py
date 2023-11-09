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
from multiprocessing import Pool, cpu_count
from ..helpers import Logger as logger

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
processes = 500
edges_per_page = 1000

def create_user_network(num_subs):
    subscribers_network.create_subscribers_network(num_subs, processes)


def assign_subscribers_to_carrier(carrier, count):
    pid, subs = os.getpid(), []
    logger.default(pid, "Assigning", count, "subscribers to carrier", carrier)
    for _ in range(count):
        subs.append(make_subscriber(carrier))
        
    save_subscribers(subs)
            
def assign_subscribers_process(args):
    index, shares, num_subs = args
    for i, share in enumerate(shares):
        carrier = index * len(shares) + i 
        count = round(num_subs * share)
        assign_subscribers_to_carrier(carrier, count) 
        
def make_subscriber(carrier):
    npa = random.randint(200, 999)
    nxx = random.randint(100, 999)
    num = str(random.randint(0, 9999)).zfill(4)
    
    return carrier, f"{carrier}:{npa}-{nxx}-{num}"

            
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

def assign_subscribers(num_subs):
    pool = Pool(processes=processes)
    chunks = np.array_split(market_shares, processes)
    chunks = [(index, chunk, num_subs) for index, chunk in enumerate(chunks)]
    pool.map(assign_subscribers_process, chunks)
    
def init_user_network(num_subs):
    timed(assign_subscribers)(num_subs)
    timed(create_user_network)(num_subs)
 
def fresh_start(num_carriers):
    init_phone_network(num_carriers)
    set_cache()

def save_subscribers(items):
    data = []
    batch = 0
    pid = os.getpid()
    
    for index, (carrier, phone) in enumerate(items):
        id = uuid4()
        data.append([str(id), str(phone), str(carrier)])
        
        if index > 0 and index % 10000 == 0:
            batch += 1
            print(f'-> Saving Subscribers: pid({pid}) > Batch {batch} > Total saved: {id}')
            database.save_subscribers(data)
            data = []      
            
    if len(data) > 0:
        logger.default(f'Saving Subscribers: pid({pid}) > Batch {batch} > Total saved: {id}')
        database.save_subscribers(data)

def make_raw_cdrs():
    num_pages = database.get_number_of_pages_in_edges(per_page=edges_per_page)
    logger.info(f'Generating CDRs: Total pages: {num_pages}')
    pages = np.arange(num_pages)
    pool = Pool(processes=processes)
    pool.map(make_raw_cdrs_worker, pages)



def make_raw_cdrs_worker(page):
    pid = os.getpid()
    edges = database.get_paginated_edges(page, edges_per_page)
    
    idmap = {}
    for id, src, dst in edges:
        idmap[src], idmap[dst] = True, True
        
    logger.default(f'pid({pid}) > Page {page} > Total edges: {len(edges)}')