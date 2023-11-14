from privytrace import helpers, oprf
from pygroupsig import groupsig, constants
from blspy import (BasicSchemeMPL, PrivateKey)
from privytrace import helpers
import argparse
from datetime import datetime
from oblivious.ristretto import point

num_runs = 10
groupsig.init(constants.BBS04_CODE, 0)
gkeys = groupsig.setup(constants.BBS04_CODE)
m1 = groupsig.join_mgr(0, gkeys['mgrkey'], gkeys['grpkey'], gml = gkeys['gml'])
m2 = groupsig.join_mem(1, gkeys['grpkey'], msgin = m1)
gusk = m2['memkey']
helpers.create_csv('bench.csv', 'test_name,runs,duration_in_ms', mode='a')

def exp_bench_setups():
    # Group setup
    start = helpers.startStopwatch()
    for i in range(num_runs):
        ks = groupsig.setup(constants.BBS04_CODE)
    test_name, duration = helpers.endStopwatch('gm.setup', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{duration}')
    
    # Provider registration to GM
    start = helpers.startStopwatch()
    for i in range(num_runs):
        groupsig.init(constants.BBS04_CODE, 0)
        msg1 = groupsig.join_mgr(0, gkeys['mgrkey'], gkeys['grpkey'], gml = gkeys['gml'])
        msg2 = groupsig.join_mem(1, gkeys['grpkey'], msgin = msg1)
    test_name, duration = helpers.endStopwatch('gm.register', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{duration}')
    
    # Label setup
    start = helpers.startStopwatch()
    for i in range(num_runs):
        key = oprf.keygen()
    test_name, duration = helpers.endStopwatch('lm.setup', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{duration}')
    
    # Trace Authority setup
    start = helpers.startStopwatch()
    for i in range(num_runs):
        seed: bytes = helpers.random_bytes(32)
        sk: PrivateKey = BasicSchemeMPL.key_gen(seed)
        pk = sk.get_g1()
    test_name, duration = helpers.endStopwatch('ta.setup', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{duration}')

def bench_label_generation():
    # Label generation
    label = "+19238192831|+19238192832|" + str(int(datetime.now().timestamp()))
    x = point.hash(label.encode())
    start = helpers.startStopwatch()
    
    for i in range(num_runs):
        key = oprf.keygen()
        label = oprf.eval(key, x)
        
    test_name, duration = helpers.endStopwatch('lm.eval', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{duration}')
    
def bench_signing():
    random_ct = helpers.random_bytes(1024) # 1KB
    random_label = helpers.random_bytes(32)
    
    # Sign
    start = helpers.startStopwatch()
    for i in range(num_runs):
        msg = groupsig.sign(random_ct + random_label, gusk, gkeys['grpkey'])
    test_name, duration = helpers.endStopwatch('gm.sign', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{duration}')
    
def bench_group_verification():
    sigmas, payloads = [],[]
    for i in range(num_runs):
        payload = helpers.random_bytes(1056)
        sigma = groupsig.sign(payload, gusk, gkeys['grpkey'])
        sigmas.append(sigma)
        payloads.append(payload)
    
    # Verify
    start = helpers.startStopwatch()
    for i in range(num_runs):
        groupsig.verify(sigmas[i], payloads[i], gkeys['grpkey'])
    
    test_name, duration = helpers.endStopwatch('gm.verify', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{duration}')
    
def bench_bls_signing():
    sk = BasicSchemeMPL.key_gen(helpers.random_bytes(32))
    pk = sk.get_g1()
    
    labels = []
    for i in range(num_runs):
        label = helpers.random_bytes(32)
        labels.append(label)
    
    # Sign
    start = helpers.startStopwatch()
    for i in range(num_runs):
        sig = BasicSchemeMPL.sign(sk, labels[i])
    test_name, duration = helpers.endStopwatch('bls.sign', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{duration}')
    

def init(args):
    if args.all:
        helpers.create_csv('bench.csv', 'test_name,runs,duration_in_ms', mode='w')
        
    if args.setup or args.all:
        exp_bench_setups()
    if args.lbl_gen or args.all:
        bench_label_generation()
    if args.grp_sign or args.all:
        bench_signing()
    if args.grp_verify or args.all:
        bench_group_verification()
    if args.bls or args.all:
        bench_bls_signing()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run experiments')
    parser.add_argument('-s', '--setup',  action='store_true', help='Run setup experiment', required=False)
    parser.add_argument('-lg', '--lbl_gen',  action='store_true', help='Run label generation experiment', required=False)
    parser.add_argument('-gs', '--grp_sign',  action='store_true', help='Run group signature experiment', required=False)
    parser.add_argument('-gv', '--grp_verify', action='store_true', help='Run group verification experiment', required=False)
    parser.add_argument('-a', '--all', action='store_true', help='Run all', required=False)
    parser.add_argument('-b', '--bls', action='store_true', help='Run BLS signature', required=False)
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
    else:
        init(args)