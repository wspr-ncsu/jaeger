import os, json
import argparse
import numpy as np
import traceback as extb
from multiprocessing import Pool
from jager.helpers import CDR
import jager.groupsig as groupsig
from jager.datagen import database
import jager.trace_auth as trace_auth
from jager.datagen.helpers import timed
import jager.contribution as contribution
import jager.helpers as helpers
import jager.label_mgr as label_mgr
import benchmarks

processes=8
batch_size = 1000
group_sig = { 'gpk': groupsig.get_gpk(), 'mems': {}}
tapk = trace_auth.get_public_key()
lm_sk = label_mgr.load_sk()
    
def load_carrier_group_member_keys():
    global group_sig
    with open('membership-keys.json', 'r') as f:
        keys = json.load(f)
        for carrier in keys:
            group_sig['mems'][carrier] = groupsig.client_import_usk(keys[carrier])
        
def get_cdrs(round, num_records, pages):
    cdrs = database.get_cdrs(round, num_records)
    print(f'Loaded {len(cdrs)} records...')
    return np.array_split(cdrs, pages)
    
def contribute(records):
    pid = os.getpid()
    print(f'[{pid}] Contributing {len(records)} records...')
    
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
                'usk': group_sig['mems'][str(carrier)]
            }, tapk=tapk, lm_sk=lm_sk, over_http=False, cdrs=cdrs[carrier])
            
            # database.mark_cdrs_as_contributed("','".join([str(c.id) for c in batch]))
        except Exception as e:
            print(e)
            extb.print_exc()
    
def bench_query(size):
    num_runs, lines = 100, []
    
    for i in range(num_runs):
        start = helpers.startStopwatch()
        database.find_ct_records_by_random_label()
        test_name, tdur, adur = helpers.endStopwatch('db.fetch', start, 1, silent=True)
        lines.append(f'{test_name},{i},{adur},{size}')
        
    helpers.update_csv('queries.csv', "\n".join(lines))

def bench_insertion(size):
    num_runs, lines = 100, []
    label, ct, sigma = benchmarks.random_contribution()
    label = label.hex()
    
    for i in range(num_runs):
        start = helpers.startStopwatch()
        database.insert_ct_records(label, ct, sigma)
        test_name, tdur, adur = helpers.endStopwatch('db.insert', start, 1, silent=True)
        lines.append(f'{test_name},{i},{adur},{size}')
        
    database.delete_ct_records_by_label(label)
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
    bench_insertion(ct_records_size)
            
def create_csv_files(mode='a'):
    helpers.create_folder_if_not_exists('results')
    helpers.create_csv('db_stats.csv', 'table,size,rows', mode)
    helpers.create_csv('queries.csv', 'test_name,index,duration_in_ms,size', mode)
    
def init(args):
    print('Loading carrier group member secret keys...')
    timed(load_carrier_group_member_keys)()
    num_chunks_in_batch = args.records // 1000
    num_chunks_in_batch = num_chunks_in_batch if num_chunks_in_batch > 0 else 1
    
    create_csv_files('w' if args.clean else 'a')
    
    with Pool(processes=processes) as pool:
        for batch in range(0, args.batches):
            print(f'[R-{batch}] Loading {args.records} records...')
            chunks = get_cdrs(batch, args.records, num_chunks_in_batch)
            pool.map(contribute, chunks)
        
            save_stats() # save db stats
        
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run contribution and tracebacks')
    parser.add_argument('-b', '--batches', type=int, help='Number of batches', required=False, default=1)
    parser.add_argument('-r', '--records', type=int, help='Number of cdrs per batch to contribute', required=True)
    parser.add_argument('-c', '--clean', action='store_true', help='Clean existing results', required=False, default=False)
    args = parser.parse_args()
    
    init(args)