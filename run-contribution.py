import os
import argparse
import numpy as np
import traceback as extb
from multiprocessing import Pool
from privytrace.helpers import CDR
from privytrace.helpers import Logger
import privytrace.groupsig as groupsig
from privytrace.datagen import database
import privytrace.trace_auth as trace_auth
from privytrace.datagen.helpers import timed
import privytrace.contribution as contribution
import privytrace.helpers as helpers
import privytrace.label_mgr as label_mgr

processes=24
batch_size = 1000
group_sig = { 'gpk': groupsig.get_gpk(), 'mems': {}}
tapk = trace_auth.get_public_key()
lm_sk = label_mgr.server_setup()
    
def load_carrier_group_member_keys():
    for carrier in range(7000):
        keys = groupsig.client_register(carrier)
        group_sig['mems'][str(carrier)] = keys['usk']
        
def get_cdrs(round, num_records, pages):
    cdrs = database.get_cdrs(round, num_records)
    return np.array_split(cdrs, pages)
    
def contribute(records):
    pid = os.getpid()
    Logger.info(f'[{pid}] Contributing {len(records)} records...')
    
    cdrs = {}
    
    # group cdrs by carrier
    for record in records:
        record = CDR(*record)
        if record.curr not in cdrs:
            cdrs[record.curr] = []
        cdrs[record.curr].append(record)
        
    # run contribution for each carrier
    for carrier in cdrs:
        try:
            contribution.contribute(group={
                'gpk': group_sig['gpk'],
                'usk': group_sig['mems'][carrier]
            }, tapk=tapk, lm_sk=lm_sk, over_http=False, cdrs=cdrs[carrier])
            
            # database.mark_cdrs_as_contributed("','".join([str(c.id) for c in batch]))
        except Exception as e:
            Logger.error(e)
            extb.print_exc()
    
def bench_query(size):
    num_runs, lines = 100, []
    
    for i in range(num_runs):
        start = helpers.startStopwatch()
        database.find_ct_records_by_random_label()
        test_name, duration = helpers.endStopwatch('fetch', start, 1, silent=True)
        lines.append(f'{test_name},{i},{duration},{size}')
        
    helpers.update_csv('queries.csv', "\n".join(lines))
    

def save_stats():
    tables = ['ct_records']
    stats = database.get_table_sizes()
    lines = []
    ct_records_size = None
    
    for item in stats:
        if item[0] in tables:
            lines.append(f'{item[0]},{item[1]}, {item[2]}')
            if item[0] == 'ct_records':
                ct_records_size = item[1]

    helpers.update_csv('db_stats.csv', "\n".join(lines))
    
    bench_query(ct_records_size)
            
def create_csv_files(mode='a'):
    helpers.create_csv('db_stats.csv', 'table,size,rows', mode)
    helpers.create_csv('queries.csv', 'test_name,index,duration_in_ms,size', mode)
    
def init(args):
    Logger.info('Loading carrier group member secret keys...')
    timed(load_carrier_group_member_keys)()
    num_pages = args.records // 1000
    
    create_csv_files('w' if args.clean else 'a')
    
    with Pool(processes=processes) as pool:
        for round in range(10, args.rounds):
            Logger.info(f'[R-{round}] Loading {args.records} records...')
            
            chunks = get_cdrs(round, args.records, num_pages)
            pool.map(contribute, chunks)
        
            save_stats() # save db stats
        
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run contribution and tracebacks')
    parser.add_argument('-r', '--rounds', type=int, help='Number of rounds', required=False, default=1)
    parser.add_argument('-n', '--records', type=int, help='Number of cdrs to contribute', required=False)
    parser.add_argument('-c', '--clean', action='store_true', help='Clean existing results', required=False, default=False)
    args = parser.parse_args()
    
    init(args)