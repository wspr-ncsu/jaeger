import privytrace.datagen.generator as generator
import models.database as db
import argparse
from dotenv import load_dotenv

load_dotenv()

def run_phone_network(num_carriers):
    generator.init_phone_network(num_carriers=num_carriers)
    db.save('shortest_paths', generator.shortest_paths) if db.connect() else None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup simulation base data')
    net_help = 'Compute Phone network and all pairs shortest paths. Value is number of carriers'
    parser.add_argument('-n', '--network', type=int, help=net_help, required=False)
    args = parser.parse_args()
    print(args)
    
    if args.network:
        run_phone_network(args.network)