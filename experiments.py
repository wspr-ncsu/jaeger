from privytrace import helpers, oprf
from pygroupsig import groupsig, constants
from blspy import (BasicSchemeMPL, PrivateKey)
from privytrace import helpers
import argparse

num_runs = 1000

def exp_bench_setups():
    helpers.create_csv('setup.csv', 'test_name,runs,duration(ms)')
    
    # Group setup
    start = helpers.startStopwatch()
    for i in range(num_runs):
        gsetup = groupsig.setup(constants.BBS04_CODE)
    test_name, duration = helpers.endStopwatch('gm.setup', start, num_runs)
    helpers.update_csv('setup.csv', f'{test_name},{num_runs},{duration}')
    
    # Provider registration to GM
    start = helpers.startStopwatch()
    for i in range(num_runs):
        groupsig.init(constants.BBS04_CODE, 0)
        msg1 = groupsig.join_mgr(0, gsetup['mgrkey'], gsetup['grpkey'], gml = gsetup['gml'])
        msg2 = groupsig.join_mem(1, gsetup['grpkey'], msgin = msg1)
    test_name, duration = helpers.endStopwatch('gm.register', start, num_runs)
    helpers.update_csv('setup.csv', f'{test_name},{num_runs},{duration}')
    
    # Label setup
    start = helpers.startStopwatch()
    for i in range(num_runs):
        key = oprf.keygen()
    test_name, duration = helpers.endStopwatch('lm.setup', start, num_runs)
    helpers.update_csv('setup.csv', f'{test_name},{num_runs},{duration}')
    
    # Trace Authority setup
    start = helpers.startStopwatch()
    for i in range(num_runs):
        seed: bytes = helpers.random_bytes(32)
        sk: PrivateKey = BasicSchemeMPL.key_gen(seed)
        pk = sk.get_g1()
    test_name, duration = helpers.endStopwatch('ta.setup', start, num_runs)
    helpers.update_csv('setup.csv', f'{test_name},{num_runs},{duration}')

def init(args):
    if args.setup:
        exp_bench_setups()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run experiments')
    parser.add_argument('-s', '--setup',  action='store_true', help='Run setup experiment', required=False)
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
    else:
        init(args)