from jager.helpers import CDR
import jager.groupsig as groupsig
import jager.trace_auth as trace_auth
import jager.traceback as traceback
import argparse, json
import jager.analyzer as analyzer
from uuid import uuid4

carrier_usks = {}
tapk = trace_auth.get_public_key()

def load_carrier_group_member_keys():
    global carrier_usks
    with open('membership-keys.json', 'r') as f:
        keys = json.load(f)
        for carrier in keys:
            carrier_usks[str(carrier)] = groupsig.client_import_usk(keys[carrier])

def trace(src, dst, ts, carrier):
    cdr = CDR(id=str(uuid4()), src=src, dst=dst, ts=ts)
    cgroup = {
        'usk': carrier_usks[carrier],
        'gpk': groupsig.get_gpk()
    }
    records = traceback.trace(group=cgroup, tapk=tapk, cdrs=[cdr])
    print(records)
    analyzer.init(records)
    analyzer.analyze()

def init(args):
    load_carrier_group_member_keys()
    trace(args.src, args.dst, args.ts, args.carrier)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a trace on a CDR')
    parser.add_argument('-t', '--ts', type=str, help='Call time', required=True)
    parser.add_argument('-s', '--src', type=str, help='Source telephone number', required=True)
    parser.add_argument('-d', '--dst', type=str, help='Destination telephone number', required=True)
    parser.add_argument('-c', '--carrier', type=str, help='Carrier making this trace', default=1)
    
    args = parser.parse_args()
    
    init(args)