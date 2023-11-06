from privytrace import helpers, oprf
from pygroupsig import groupsig, constants
from blspy import (BasicSchemeMPL, PrivateKey)

num_runs = 1000

def exp_bench_setups():
    # Group setup
    start = helpers.startStopwatch()
    for i in range(num_runs):
        gsetup = groupsig.setup(constants.BBS04_CODE)
    helpers.endStopwatch('gm.setup', start, num_runs)
    
    # Provider registration to GM
    start = helpers.startStopwatch()
    for i in range(num_runs):
        groupsig.init(constants.BBS04_CODE, 0)
        msg1 = groupsig.join_mgr(0, gsetup['mgrkey'], gsetup['grpkey'], gml = gsetup['gml'])
        msg2 = groupsig.join_mem(1, gsetup['grpkey'], msgin = msg1)
    helpers.endStopwatch('gm.register', start, num_runs)
    
    # Label setup
    start = helpers.startStopwatch()
    for i in range(num_runs):
        key = oprf.keygen()
    helpers.endStopwatch('lm.setup', start, num_runs)
    
    # Trace Authority setup
    start = helpers.startStopwatch()
    for i in range(num_runs):
        seed: bytes = helpers.random_bytes(32)
        sk: PrivateKey = BasicSchemeMPL.key_gen(seed)
        pk = sk.get_g1()
    helpers.endStopwatch('ta.setup', start, num_runs)

def bench_encryptions():
    pass