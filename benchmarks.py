from jager import helpers, oprf
from pygroupsig import groupsig, constants, signature
from blspy import (BasicSchemeMPL, PrivateKey)
from jager import helpers, analyzer
import argparse
from datetime import datetime
from oblivious.ristretto import point
from jager import witenc
from jager.datagen import generator
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

def exp_bench_setups():
    lines = []
    # Group setup
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        ks = groupsig.setup(constants.BBS04_CODE)
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'Group Manager,setup & keygen', istart, 1, True)
        lines.append(f'{itest_name},{i},{i_tdur},{i_adur}')
        
    test_name, t_dur, a_dur = helpers.endStopwatch('Group Manager,setup & keygen', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    
    # Provider registration to GM
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        
        groupsig.init(constants.BBS04_CODE, 0)
        msg1 = groupsig.join_mgr(0, gkeys['mgrkey'], gkeys['grpkey'], gml = gkeys['gml'])
        msg2 = groupsig.join_mem(1, gkeys['grpkey'], msgin = msg1)
        
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'Group Manager,register provider', istart, 1, True)
        lines.append(f'{itest_name},{i},{i_tdur},{i_adur}')
        
    test_name, t_dur, a_dur = helpers.endStopwatch('Group Manager,register provider', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    
    # Label setup
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        key = oprf.keygen()
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'Label Manager,setup & keygen', istart, 1, True)
        lines.append(f'{itest_name},{i},{i_tdur},{i_adur}')
        
    test_name, t_dur, a_dur = helpers.endStopwatch('Label Manager,setup & keygen', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    
    # Trace Authority setup
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        seed: bytes = helpers.random_bytes(32)
        sk: PrivateKey = BasicSchemeMPL.key_gen(seed)
        pk = sk.get_g1()
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'Trace Authority,setup & keygen', istart, 1, True)
        lines.append(f'{itest_name},{i},{i_tdur},{i_adur}')
    test_name, t_dur, a_dur = helpers.endStopwatch('Trace Authority,setup & keygen', start, num_runs)
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
        
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'Label Manager,PRF evaluation', istart, 1, True)
        lines.append(f'{itest_name},{i},{i_tdur},{i_adur}')
        
    test_name, t_dur, a_dur = helpers.endStopwatch('Label Manager,PRF evaluation', start, num_runs)
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
        
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'Group Manager,gsign', istart, 1, True)
        lines.append(f'{itest_name},{i},{i_tdur},{i_adur}')
        
    test_name, t_dur, a_dur = helpers.endStopwatch('Group Manager,gsign', start, num_runs)
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
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'Group Manager,gverify', istart, 1, True)
        lines.append(f'{itest_name},{i},{i_tdur},{i_adur}')
    
    test_name, t_dur, a_dur = helpers.endStopwatch('Group Manager,gverify', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    helpers.update_csv('index-timings.csv', '\n'.join(lines))
    
def bench_group_sig_open():
    lines = []
    payload = helpers.random_bytes(2048)
    sigma = groupsig.sign(payload, gusk, gkeys['grpkey'])
    
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        groupsig.open(sigma, gkeys['mgrkey'], gkeys['grpkey'], gml = gkeys['gml'])
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'Group Manager,open', istart, 1, True)
        lines.append(f'{itest_name},{i},{i_tdur},{i_adur}')
    
    test_name, t_dur, a_dur = helpers.endStopwatch('Group Manager,open', start, num_runs)
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
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'Trace Authority,sign', istart, 1, True)
        lines.append(f'{itest_name},{i},{i_tdur},{i_adur}')
    test_name, t_dur, a_dur = helpers.endStopwatch('Trace Authority,sign', start, num_runs)
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
        label = generate_label(call).encode('utf-8')
        istart = helpers.startStopwatch()
        we_istart = helpers.startStopwatch()
        ct = witenc.client_encrypt(pk=trace_auth_pk, label=label, cdr=hops)
        ct = witenc.client_export_ct(ct)
        we_itest_name, we_i_tdur, we_i_adur = helpers.endStopwatch(f'Carrier,Enc', we_istart, 1, True)
        sigma = groupsig.sign(f'{label}|{ct}', gusk, gkeys['grpkey'])
        sigma = signature.signature_export(sigma)
        cts.append(ct)
        
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'Carrier,contribution', istart, 1, True)
        lines.append(f'{itest_name},{i},{i_tdur},{i_adur}')
        lines.append(f'{we_itest_name},{i},{we_i_tdur},{we_i_adur}')
        
    test_name, t_dur, a_dur = helpers.endStopwatch('Carrier,contribution', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        sig = BasicSchemeMPL.sign(trace_auth_sk, label)
        we_istart = helpers.startStopwatch()
        ct_i = witenc.client_import_ct(cts[i])
        msg = witenc.client_decrypt(sig=sig, ct=ct_i, decode=False)
        we_itest_name, we_i_tdur, we_i_adur = helpers.endStopwatch(f'Carrier,Dec', we_istart, 1, True)
        
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'Carrier,trace', istart, 1, True)
        lines.append(f'{itest_name},{i},{i_tdur},{i_adur}')
        lines.append(f'{we_itest_name},{i},{we_i_tdur},{we_i_adur}')
        
    test_name, t_dur, a_dur = helpers.endStopwatch('Carrier,trace', start, num_runs)
    helpers.update_csv('bench.csv', f'{test_name},{num_runs},{t_dur},{a_dur}')
    helpers.update_csv('index-timings.csv', '\n'.join(lines))

def bench_analysis():
    lines = []
    ideal = ['None|1|2',    '1|2|3',    '2|3|4',    '3|4|5',    '4|5|None']
    
    start = helpers.startStopwatch()
    for i in range(num_runs):
        istart = helpers.startStopwatch()
        analyzer.init(ideal, False)
        analyzer.analyze()
        itest_name, i_tdur, i_adur = helpers.endStopwatch(f'Group Manager,Faulty set', istart, 1, True)
        lines.append(f'{itest_name},{i},{i_tdur},{i_adur}')
        
    test_name, t_dur, a_dur = helpers.endStopwatch('Group Manager,Faulty set', start, num_runs)
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
        print('Cache file not found. Please regenerate network')
        return
        
    print('Loading phone network metadata from cache...')
    generator.load_cache()
    
    total, count = 0, 0
    
    num_carriers = len(generator.phone_network.nodes)
    carriers = list(range(num_carriers))
    carriers = [(i, num_carriers) for i in carriers]
    pool = Pool(processes=24)
    
    print('Calculating average number of hops...')
    total = sum(pool.map(get_hops, carriers))
    count = num_carriers * (num_carriers - 1)
    avg = total // count
    
    helpers.update_csv('keyval.csv', f'average_hops,{avg}')
    print(f'Average number of hops: {avg}')

def generate_label(call):
    key = oprf.keygen()
    s, x = oprf.mask(call)
    fx = oprf.eval(key, x)
    return oprf.export_point(oprf.unmask(s, fx))

def init(args):
    header = 'category,test_name,runs,total_duration_in_ms,avg_duration_in_ms'
    helpers.create_folder_if_not_exists('results')
    helpers.create_csv('bench.csv', header, mode='a')
    helpers.create_csv('index-timings.csv', header, mode='a')
    helpers.create_csv('keyval.csv', 'key,val', mode='a')

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
    if args.grp_open or args.all:
        bench_group_sig_open()
    if args.hops:
        get_avg_num_of_hops()
    if args.analysis or args.all:
        bench_analysis()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run experiments')
    parser.add_argument('-s', '--setup',  action='store_true', help='Run setup experiment', required=False)
    parser.add_argument('-lg', '--lbl_gen',  action='store_true', help='Run label generation experiment', required=False)
    parser.add_argument('-gs', '--grp_sign',  action='store_true', help='Run group signature experiment', required=False)
    parser.add_argument('-go', '--grp_open',  action='store_true', help='Run group signature open', required=False)
    parser.add_argument('-gv', '--grp_verify', action='store_true', help='Run group verification experiment', required=False)
    parser.add_argument('-a', '--all', action='store_true', help='Run all', required=False)
    parser.add_argument('-b', '--bls', action='store_true', help='Run BLS signature', required=False)
    parser.add_argument('-e', '--enc', action='store_true', help='Run encryption', required=False)
    parser.add_argument('-ah', '--hops', action='store_true', help='Run average number of hops', required=False)
    parser.add_argument('-an', '--analysis', action='store_true', help='Run analysis', required=False)
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
    else:
        init(args)