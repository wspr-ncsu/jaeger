from jager.helpers import CDR
import jager.groupsig as groupsig
import jager.trace_auth as trace_auth
import jager.traceback as traceback
from blspy import G1Element
import argparse
import jager.analyzer as analyzer

tapk: G1Element = trace_auth.request_registration()

def trace(args):
    cdr = CDR(src=args.src, dst=args.dst, ts=args.ts)
    cgroup = groupsig.client_register(args.carrier)
    records = traceback.trace(group=cgroup, tapk=tapk, cdrs=[cdr])
    print(records)
    analyzer.init(records)
    analyzer.analyze()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a trace on a CDR')
    parser.add_argument('-t', '--ts', type=str, help='Call time', required=True)
    parser.add_argument('-s', '--src', type=str, help='Source telephone number', required=True)
    parser.add_argument('-d', '--dst', type=str, help='Destination telephone number', required=True)
    parser.add_argument('-c', '--carrier', type=str, help='Carrier making this trace', required=True)
    
    args = parser.parse_args()
    
    trace(args)