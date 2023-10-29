from privytrace.helpers import CDR
import privytrace.groupsig as groupsig
import privytrace.trace_auth as trace_auth
import privytrace.contribution as contribution
import privytrace.traceback as traceback
from blspy import G1Element
import argparse
from privytrace.datagen import generator
from privytrace.helpers import Logger
from privytrace.datagen import database

groups = {}
tapk: G1Element = trace_auth.request_registration()

def get_carrier_groupsig(carrier):
    if carrier not in groups:
        groups[carrier] = groupsig.client_register(carrier)
        
    return groups[carrier]

def store_records(cdrs):
    database.save_cdrs(cdrs)

def run_contribution(args):
    if args.network:
        Logger.info('Generating phone network...')
        generator.fresh_start(args.network)
    else:
        if generator.cache_file.exists():
            Logger.info('Loading phone network metadata from cache...')
            generator.load_cache()
        else:
            Logger.error('Cache file not found. Please run with -n option to generate phone network.')
            return
        
    generator.init_user_network(args.subscribers)
    generate()
    
def generate():
    temp = []
    print(len(generator.phone_network.edges))
    for index, (src_i, dst_i) in enumerate(generator.phone_network.edges):
        src, dst = generator.subscribers[src_i], generator.subscribers[dst_i]
        cdrs = generator.simulate_call(src, dst)
        
        if cdrs is None:
            continue
        
        print('Storing {} CDRs from {} to {}'.format(len(cdrs), src, dst))
        store_records(cdrs)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run contribution and tracebacks')
    parser.add_argument('-n', '--network', type=int, help='Number of phone networks', required=False)
    parser.add_argument('-s', '--subscribers', type=int, help='Number of subscribers', required=True)
    args = parser.parse_args()
    
    run_contribution(args)
    
            