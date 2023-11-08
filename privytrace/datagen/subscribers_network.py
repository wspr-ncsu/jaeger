import networkx as nx
import numpy as np
import random
from datetime import datetime
import matplotlib.pyplot as plt
from .helpers import timed, get_elapsed_time
from privytrace.datagen import database
from uuid import uuid4


subscribers = None
robocallers = None
num_subnets = None

def create_subscribers_network(users, rbcallers):
    global subscribers, num_subnets, robocallers

    num_users, num_subnets = users
    subscribers = np.arange(int(num_users), dtype=int)
    robocallers = np.arange(int(rbcallers), dtype=int)

    legitimate = timed(create_individuals_network)()
    robocalls = timed(create_robocallers_network)()

    return legitimate, robocalls

def create_individuals_network():
    subnetworks = split_num_into_ratios(len(subscribers), num_subnets)
    last_index = 0

    for i, count in enumerate(subnetworks):
        calls = []
        last_index += count

        if count < 2:
            continue

        m = random.choices([1, 2], weights=[0.7, 0.3], k=1)[0]
        
        if count == m:
            count += 1
            
        start = datetime.now()
        network = nx.barabasi_albert_graph(count, m)
        indexes = np.arange(last_index - count, last_index)

        for src, dst in network.edges:
            src = indexes[src]
            dst = indexes[dst]
            calls.append([str(uuid4()), str(src), str(dst)])

        # insert calls db
        database.save_edges(calls)
        duration = get_elapsed_time(start)
        print(f'-> Created G_{i}(V={count}, m={m}). Time taken: {duration}')

    return calls


def create_robocallers_network():
    robocalls = []
    # generate random float between 0.05 and 0.12 (Who's Calling paper, Usenix Security 2020)
    size = int(len(subscribers) * random.uniform(0.05, 0.12))
    calls_count = split_num_into_ratios(size, len(robocallers))
    # print(calls_count)
    print(f'-> Creating robocallers network with {size} calls')
    for i, count  in enumerate(calls_count):
        calls = make_robocalls(robocallers[i], count)
        robocalls.extend(calls) if calls is not None else None

    return robocalls

def make_robocalls(caller, num_subs):
    if num_subs == 0:
        return None

    calls = []
    destinations = np.random.choice(subscribers, num_subs, replace=False)
    for dst in destinations:
        src = spoof_caller_id(caller)
        calls.append((src, dst))

    return calls

def split_num_into_ratios(N, m):
    ratios = []
    for i in range(m):
        ratios.append(random.uniform(0, 5))
    total = sum(ratios)
    for i in range(m):
        ratios[i] = int(ratios[i] / total * N)
    return ratios

def register_subscribers(carrier_id, num_subs, cc = 1):
    num_subs, subs = int(num_subs), []

    for _ in range(num_subs):
        phone = npa_nxx_xxxx(cc)
        subs.append(f'{carrier_id},{phone}')
    return subs

def npa_nxx_xxxx(cc):
    npa = random.randint(200, 999)
    nxx = random.randint(200, 999)
    # num should be 4 digits, from 0000 to 9999
    num = str(random.randint(0, 9999)).zfill(4)
    return f"+{cc} {npa}-{nxx}-{num}"

def spoof_caller_id(caller):
    return caller

def draw_graph(edges):
    G = nx.Graph()
    G.add_edges_from(edges)

    # Draw the graph using Matplotlib
    nx.draw(G, with_labels=True, node_color='lightblue', font_weight='bold', font_size=6)
    plt.show()