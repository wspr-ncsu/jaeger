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

processes=2
batch_size = 100
group_sig = { 'gpk': groupsig.get_gpk(), 'mems': {}}
tapk = trace_auth.request_registration()
    
def load_carrier_group_member_keys():
    for carrier in range(7000):
        keys = groupsig.client_register(carrier)
        group_sig['mems'][str(carrier)] = keys['usk']
        
def get_cdrs(num_records, pages=1000):
    cdrs = database.get_cdrs(num_records)
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
        
    # chunk each carrier's cdrs into batches
    for carrier in cdrs:
        num_batches = len(cdrs[carrier])//batch_size
        
        if num_batches == 0:
            cdrs[carrier] = [cdrs[carrier]]
        else:
            cdrs[carrier] = np.array_split(cdrs[carrier], num_batches)
        
    # run contribution for each carrier
    for carrier in cdrs:
        for batch in cdrs[carrier]:
            try:
                contribution.contribute(group={
                    'gpk': group_sig['gpk'],
                    'usk': group_sig['mems'][carrier]
                }, tapk=tapk, cdrs=batch)
                
                database.mark_cdrs_as_contributed(batch)
            except Exception as e:
                Logger.error(e)
                extb.print_exc()

def bench_query(size):
    helpers.create_csv('queries.csv', 'test_name,runs,duration_in_ms,size')
    
    num_runs = 100
    start = helpers.startStopwatch()
    for i in range(num_runs):
        database.find_ct_records_by_random_label()
    test_name, duration = helpers.endStopwatch('fetch', start, num_runs)
    helpers.update_csv('queries.csv', f'{test_name},{num_runs},{duration},{size}')
    

def save_stats():
    helpers.create_csv('db_stats.csv', 'table,size,rows')
    tables = ['ct_records']
    stats = database.get_table_sizes()
    
    ct_records_size = None
    for item in stats:
        if item[0] in tables:
            helpers.update_csv('db_stats.csv', f'{item[0]},{item[1]}, {item[2]}')
            if item[0] == 'ct_records':
                ct_records_size = item[1]
                
    bench_query(ct_records_size)
            
    
def init(args):
    Logger.info('Loading carrier group member secret keys...')
    timed(load_carrier_group_member_keys)()
    num_pages = args.records // 1000
    
    for i in range(args.rounds):
        Logger.info(f'[Round {i}] Loading {args.records} records...')
        chunks = get_cdrs(args.records, num_pages)
        pool = Pool(processes=processes)
        pool.map(contribute, chunks)
        pool.close()
        
        save_stats() # save db stats
        
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run contribution and tracebacks')
    parser.add_argument('-r', '--rounds', type=int, help='Number of rounds', required=False, default=1)
    parser.add_argument('-n', '--records', type=int, help='Number of cdrs to contribute', required=False)
    args = parser.parse_args()
    
    init(args)