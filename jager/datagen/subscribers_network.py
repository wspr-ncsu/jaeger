import os
import random
import numpy as np
import networkx as nx
from uuid import uuid4
from .helpers import timed
from multiprocessing import Pool
from jager.datagen import database
from ..helpers import Logger as logger

def create_subscribers_network(users, subnets, processes):
    subscribers = np.arange(int(users), dtype=int)
    u_chunks = np.array_split(subscribers, subnets)
    
    pool = Pool(processes=processes)
    pool.map(create_individuals_network, u_chunks)

def create_individuals_network(subscribers):
    n, pid = len(subscribers), os.getpid()
    logger.default(f"pid({pid})\t> creating network for {n} subscribers")
    
    m = random.choices([1, 2, 3], weights=[0.5, 0.5, 0.5], k=1)[0]
    
    if n <= m:
        return

    network = nx.barabasi_albert_graph(n, m)
    logger.default(f'pid({pid})\t> G(V={len(network.nodes)}, E={len(network.edges)}).')

    data, chunk = [], 1000
    for src, dst in network.edges:
        data.append([str(uuid4()), int(subscribers[src]), int(subscribers[dst])])
        if len(data) > chunk:
            database.save_edges(data)
            data = []
    
    if len(data) > 0:
        database.save_edges(data)
