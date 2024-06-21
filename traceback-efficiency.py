import pathlib, os, pickle
import networkx as nx # type: ignore

G = None
carriers = []
shortest_paths = None
adopters = {}
call_space = []

cache_file = pathlib.Path.cwd().joinpath('cache.pkl')

def set_cache():
    data = (G, carriers, shortest_paths, call_space)
    with open(cache_file, 'wb') as file:
        pickle.dump(data, file)

def load_cache():
    global G, carriers, shortest_paths, call_space
    if not os.path.exists(cache_file):
        return False
    with open(cache_file, 'rb') as file:
        G, carriers, shortest_paths, call_space = pickle.load(file)
    return True

def generate_phone_network(N, m):
    global G, carriers
    if G and carriers:
        return
    print('Generating phone network')
    G = nx.barabasi_albert_graph(N, m)
    degree = G.degree()
    carriers = sorted(degree, key=lambda x: x[1], reverse=True)

def all_pairs_johnson():
    global shortest_paths
    if shortest_paths:
        return
    print('Running Johnson algorithm')
    shortest_paths = nx.johnson(G)

def get_call_path(source, target):
    return shortest_paths[source][target]

def set_adopters(num_adopters = 5):
    global adopters
    adopters = {carrier[0]: True for carrier in carriers[:num_adopters]}

def is_adopter(node):
    return adopters.get(node, False)

def gen_call_space():
    global call_space

    if (len(call_space) > 0):
        return call_space
    
    print('Generating call space')

    call_space, visited = [], {}

    for (src, _) in carriers:
        for (dst, _) in carriers:
            if src == dst:
                continue
            if (src, dst) in visited or (dst, src) in visited:
                continue
            visited[(src, dst)] = True
            call_space.append((src, dst))

def send_to_jager(prev, curr, next):
    return [(prev, curr), (curr, next)]

def do_contribution(call_path):
    records = []
    n = len(call_path)
    for index, carrier in enumerate(call_path):
        if is_adopter(carrier):
            prev = next = None
            if index > 0: 
                prev = call_path[index - 1]
            if index < n - 1:
                next = call_path[index + 1]
            records.append(send_to_jager(prev=prev, curr=carrier, next=next))
    return records

def analyze_records(retrieved, call_path):
    # print('call_path:', call_path)
    # print('retrieved:', retrieved)
    constructed_path = []
    for record in retrieved:
        for (src, dst) in record:
            if src and src not in constructed_path:
                constructed_path.append(src)
            if dst and dst not in constructed_path:
                constructed_path.append(dst)
    
    if (len(constructed_path) == 0):
        return (False, False)
    
    # print('Constructed Path:', constructed_path)
    originator_found = constructed_path[0] == call_path[0]
    call_path_constructed = call_path == constructed_path

    # print('Original Path:', '->'.join([str(i) for i in call_path]))
    # print('Constructed_path:', '->'.join([str(i) for i in constructed_path]))
    # print('Originator_found:', originator_found)
    # print('Call path constructed', call_path_constructed)

    return (originator_found, call_path_constructed)

def main():
    N, m = 7000, 2
    load_cache()
    generate_phone_network(N, m)
    all_pairs_johnson()
    gen_call_space()
    set_cache()

    runs = 3
    calls = call_space
    total_calls_count = len(calls)

    for run in range(runs):
        num_adopters = int(0.1 * N * (run + 1))
        set_adopters(num_adopters=num_adopters)
        successful_tracebacks, full_path_found = 0, 0

        for (src, dst) in calls:
            call_path = get_call_path(src, dst)
            retrieved = do_contribution(call_path)

            (has_origin, has_fullpath) = analyze_records(
                retrieved=retrieved,
                call_path=call_path
            )

            successful_tracebacks += 1 if has_origin else 0
            full_path_found += 1 if has_fullpath else 0

        trace_percentage = round((successful_tracebacks / total_calls_count) * 100, 2)
        path_percentage = round((full_path_found / total_calls_count) * 100, 2)

        print(f'\n================= {round(num_adopters/N * 100, 2)}% Participation =================')
        print(f'Number of adopters: {num_adopters}/{N}')
        print(f'Successful Tracebacks: {successful_tracebacks}/{total_calls_count} ({trace_percentage}%)')
        print(f'Full Path Recovery: {full_path_found}/{total_calls_count} ({path_percentage}%)')

    
if __name__ == '__main__':
    main()