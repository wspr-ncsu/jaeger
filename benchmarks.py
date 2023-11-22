from privytrace import helpers, oprf
from pygroupsig import groupsig, constants, signature
from blspy import (BasicSchemeMPL, PrivateKey)
from privytrace import helpers
import argparse
from datetime import datetime
from oblivious.ristretto import point
from privytrace import witenc
from privytrace.datagen import generator
from privytrace.helpers import Logger
from multiprocessing import Pool

num_runs = 1000

# Group setup and join member
groupsig.init(constants.BBS04_CODE, 0)
gkeys = groupsig.setup(constants.BBS04_CODE)
m1 = groupsig.join_mgr(0, gkeys['mgrkey'], gkeys['grpkey'], gml = gkeys['gml'])
m2 = groupsig.join_mem(1, gkeys['grpkey'], msgin = m1)
gusk = m2['memkey']

# Trace Authority setup
trace_auth_sk = BasicSchemeMPL.key_gen(helpers.random_bytes(32))
trace_auth_pk = trace_auth_sk.get_g1()

header = 'test_name,runs,total_duration_in_ms,avg_duration_in_ms'
helpers.create_csv('bench.csv', header, mode='a')
helpers.create_csv('index-timings.csv', header, mode='a')
helpers.create_csv('keyval.csv', 'key,val', mode='a')

def exp_bench_setups():
    lines = []
    # Group setup
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        ks = groupsig.setup(constants.BBS04_CODE)
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'gm.setup', istart, 1, True)
        lines.append(f'{itest_name},1,{i_tdur},{i_adur}')
        
    test_name, t_dur, a_dur = helpers.endStopwatch('gm.setup', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    
    # Provider registration to GM
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        
        groupsig.init(constants.BBS04_CODE, 0)
        msg1 = groupsig.join_mgr(0, gkeys['mgrkey'], gkeys['grpkey'], gml = gkeys['gml'])
        msg2 = groupsig.join_mem(1, gkeys['grpkey'], msgin = msg1)
        
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'gm.register', istart, 1, True)
        lines.append(f'{itest_name},1,{i_tdur},{i_adur}')
        
    test_name, t_dur, a_dur = helpers.endStopwatch('gm.register', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    
    # Label setup
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        key = oprf.keygen()
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'lm.setup', istart, 1, True)
        lines.append(f'{itest_name},1,{i_tdur},{i_adur}')
        
    test_name, t_dur, a_dur = helpers.endStopwatch('lm.setup', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    
    # Trace Authority setup
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        seed: bytes = helpers.random_bytes(32)
        sk: PrivateKey = BasicSchemeMPL.key_gen(seed)
        pk = sk.get_g1()
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'ta.setup', istart, 1, True)
        lines.append(f'{itest_name},1,{i_tdur},{i_adur}')
    test_name, t_dur, a_dur = helpers.endStopwatch('ta.setup', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    helpers.update_csv('index-timings.csv', '\n'.join(lines))

def bench_label_generation():
    # Label generation
    lines = []
    call = "+19238192831|+19238192832|" + str(int(datetime.now().timestamp()))
    x = oprf.export_point(point.hash(call.encode()))
    start = helpers.startStopwatch()
    
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        x_prime = oprf.import_point(x)
        key = oprf.keygen()
        label = oprf.eval(key, x_prime)
        
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'lm.eval', istart, 1, True)
        lines.append(f'{itest_name},1,{i_tdur},{i_adur}')
        
    test_name, t_dur, a_dur = helpers.endStopwatch('lm.eval', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    helpers.update_csv('index-timings.csv', '\n'.join(lines))
    
def bench_signing():
    lines = []
    random_ct = helpers.random_bytes(1024) # 1KB
    random_label = helpers.random_bytes(32)
    
    # Sign
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        msg = groupsig.sign(random_ct + random_label, gusk, gkeys['grpkey'])
        
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'gm.sign', istart, 1, True)
        lines.append(f'{itest_name},1,{i_tdur},{i_adur}')
        
    test_name, t_dur, a_dur = helpers.endStopwatch('gm.sign', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    helpers.update_csv('index-timings.csv', '\n'.join(lines))
    
def bench_group_verification():
    lines = []
    sigmas, payloads = [],[]
    for i in range(num_runs):
        payload = helpers.random_bytes(1056)
        sigma = groupsig.sign(payload, gusk, gkeys['grpkey'])
        sigmas.append(sigma)
        payloads.append(payload)
    
    # Verify
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        groupsig.verify(sigmas[i], payloads[i], gkeys['grpkey'])
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'gm.verify', istart, 1, True)
        lines.append(f'{itest_name},1,{i_tdur},{i_adur}')
    
    test_name, t_dur, a_dur = helpers.endStopwatch('gm.verify', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    helpers.update_csv('index-timings.csv', '\n'.join(lines))
    
def bench_bls_signing():
    labels = []
    lines = []
    for i in range(num_runs):
        label = helpers.random_bytes(32)
        labels.append(label)
    
    # Sign
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        sig = BasicSchemeMPL.sign(trace_auth_sk, labels[i])
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'bls.sign', istart, 1, True)
        lines.append(f'{itest_name},1,{i_tdur},{i_adur}')
    test_name, t_dur, a_dur = helpers.endStopwatch('bls.sign', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    helpers.update_csv('index-timings.csv', '\n'.join(lines))

def random_contribution():
    call, hops = generate_cdr()
    label = generate_label(call).encode('utf-8')
    ct = witenc.client_encrypt(pk=trace_auth_pk, label=label, cdr=hops)
    ct = witenc.client_export_ct(ct)
    sigma = groupsig.sign(f'{label}|{ct}', gusk, gkeys['grpkey'])
    sigma = signature.signature_export(sigma)
    return label, ct, sigma

def bench_encryption():
    cts, lines = [], []
    call, hops = generate_cdr()
    
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        
        label = generate_label(call).encode('utf-8')
        ct = witenc.client_encrypt(pk=trace_auth_pk, label=label, cdr=hops)
        ct = witenc.client_export_ct(ct)
        sigma = groupsig.sign(f'{label}|{ct}', gusk, gkeys['grpkey'])
        sigma = signature.signature_export(sigma)
        cts.append(ct)
        
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'main.contribution(label+enc+gsign)', istart, 1, True)
        lines.append(f'{itest_name},1,{i_tdur},{i_adur}')
        
    test_name, t_dur, a_dur = helpers.endStopwatch('main.contribution(label+enc+gsign)', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        sig = BasicSchemeMPL.sign(trace_auth_sk, label)
        ct_i = witenc.client_import_ct(cts[i])
        msg = witenc.client_decrypt(sig=sig, ct=ct_i, decode=False)
        
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'main.trace(tsign+dec)', istart, 1, True)
        lines.append(f'{itest_name},1,{i_tdur},{i_adur}')
        
    test_name, t_dur, a_dur = helpers.endStopwatch('main.trace(tsign+dec)', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    helpers.update_csv('index-timings.csv', '\n'.join(lines))

def generate_cdr():
    call = "+00000000000|+11111111111|" + str(int(datetime.now().timestamp()))
    
    hops = '{}|{}|{}'.format(
        helpers.random_bytes(32, hex=True),
        helpers.random_bytes(32, hex=True),
        helpers.random_bytes(32, hex=True)
    )
    
    return call, hops.encode()

def get_hops(args):
    i, num_carriers = args
    hops = 0
    
    for j in range(num_carriers):
        if i == j:
            continue
        hops += len(generator.get_call_path(i, j))
        
    return hops
    
def get_avg_num_of_hops():
    if not generator.cache_file.exists():
        Logger.error('Cache file not found. Please regenerate network')
        
    Logger.info('Loading phone network metadata from cache...')
    generator.load_cache()
    
    total, count = 0, 0
    
    num_carriers = len(generator.phone_network.nodes)
    carriers = list(range(num_carriers))
    carriers = [(i, num_carriers) for i in carriers]
    pool = Pool(processes=24)
    
    Logger.info('Calculating average number of hops...')
    total = sum(pool.map(get_hops, carriers))
    count = num_carriers * (num_carriers - 1)
    avg = total // count
    
    helpers.update_csv('keyval.csv', f'average_hops,{avg}')
    Logger.info(f'Average number of hops: {avg}')

def generate_label(call):
    key = oprf.keygen()
    s, x = oprf.mask(call)
    fx = oprf.eval(key, x)
    return oprf.export_point(oprf.unmask(s, fx))

def init(args):
    if args.all:
        helpers.create_csv('bench.csv', header, mode='w')
        helpers.create_csv('index-timings.csv', header, mode='w')
        # helpers.create_csv('keyval.csv', 'key,val', mode='w')
        
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
    if args.enc or args.all:
        bench_encryption()
    if args.hops:
        get_avg_num_of_hops()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run experiments')
    parser.add_argument('-s', '--setup',  action='store_true', help='Run setup experiment', required=False)
    parser.add_argument('-lg', '--lbl_gen',  action='store_true', help='Run label generation experiment', required=False)
    parser.add_argument('-gs', '--grp_sign',  action='store_true', help='Run group signature experiment', required=False)
    parser.add_argument('-gv', '--grp_verify', action='store_true', help='Run group verification experiment', required=False)
    parser.add_argument('-a', '--all', action='store_true', help='Run all', required=False)
    parser.add_argument('-b', '--bls', action='store_true', help='Run BLS signature', required=False)
    parser.add_argument('-e', '--enc', action='store_true', help='Run encryption', required=False)
    parser.add_argument('-ah', '--hops', action='store_true', help='Run average number of hops', required=False)
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
    else:
        init(args)