import argparse
import jager.groupsig as groupsig
import jager.database as database

def mgr_register_all():
    carriers_map = {}
    gsign_keys = groupsig.mgr_import_keys()
    carriers = database.get_registered_carriers(DB_HOST='localhost')
    
    for cid, name in carriers:
        carriers_map[cid] = name
        
    data = []
    
    for cid in range(7000):
        if cid in carriers_map:
            continue
        print(f'Registering carrier {cid}')
        usk = groupsig.mgr_generate_member_keys(gsign_keys['msk'], gsign_keys['gpk'], gsign_keys['gml'])
        data.append([cid, f'carrier-{cid}', usk])
    
    if len(data) > 0:
        database.insert_carriers(data, DB_HOST='localhost')
        

def main(args):
    if args.carriers:
        mgr_register_all()
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Key generation')
    parser.add_argument('-c', '--carriers', action='store_true', help='Seed carriers', default=False, required=False)
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
    else:
        main(args)