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
    
def init(args):
    Logger.info('Loading carrier group member secret keys...')
    timed(load_carrier_group_member_keys)()
    num_pages = 100
    Logger.info(f'Loading {args.records} records...')
    chunks = get_cdrs(args.records, num_pages)
    
    pool = Pool(processes=processes)
    pool.map(contribute, chunks)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run contribution and tracebacks')
    parser.add_argument('-r', '--records', type=int, help='Number of cdrs to contribute', required=False)
    args = parser.parse_args()
    
    init(args)