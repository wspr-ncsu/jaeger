import argparse
from jager.datagen import generator
from jager.datagen import database

def init(args):
    if args.network:
        if not args.subscribers:
            print('Please specify number of subscribers with -s option.')
            return
        
        print('Generating phone network...')
        generator.fresh_start(args.network)
    else:
        if generator.cache_file.exists():
            print('Loading phone network metadata from cache...')
            generator.load_cache()
        else:
            print('Cache file not found. Please run with -n option to generate phone network.')
            return
    
    if args.subscribers:
        if database.records_exists():
            if not args.yes:
                print('Records already exist. Do you want to overwrite? (y/n)')
                choice = input()
                if choice.lower() != 'y':
                    print('Aborting...')
                    return
        print('Generating subscribers...')
        database.truncate(['subscribers', 'edges', 'raw_cdrs'])
        generator.init_user_network(args.subscribers, args.subnets)
        
    if args.cdrs:
        generator.make_raw_cdrs()
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Data generation')
    parser.add_argument('-n', '--network', type=int, help='Generate network graph of n nodes', required=False)
    parser.add_argument('-s', '--subscribers', type=int, help='Generate subscribers graph of s nodes', required=False)
    parser.add_argument('-g', '--subnets', type=int, help='Number of subnetworks for users graph', required=False, default=50)

    parser.add_argument('-c', '--cdrs', action='store_true', help='Generate cdrs from edges and subscribers', required=False)
    parser.add_argument('-y', '--yes', action='store_true', help='Overwrite existing', default=False, required=False)
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
    else:
        init(args)
    
    
            