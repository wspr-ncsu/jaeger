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

def init(args):
    if args.network:
        if not args.subscribers:
            Logger.error('Please specify number of subscribers with -s option.')
            return
        
        Logger.info('Generating phone network...')
        generator.fresh_start(args.network)
    else:
        if generator.cache_file.exists():
            Logger.info('Loading phone network metadata from cache...')
            generator.load_cache()
        else:
            Logger.error('Cache file not found. Please run with -n option to generate phone network.')
            return
    
    if args.subscribers:
        Logger.info('Generating subscribers...')
        database.truncate(['subscribers', 'edges'])
        generator.init_user_network(args.subscribers)
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run contribution and tracebacks')
    parser.add_argument('-n', '--network', type=int, help='Number of phone networks', required=False)
    parser.add_argument('-s', '--subscribers', type=int, help='Number of subscribers', required=False)
    # parser.add_argument('-g', '--subnets', type=int, help='Number of subnets for subs network', required=False, default=50)
    args = parser.parse_args()
    
    init(args)
    
            