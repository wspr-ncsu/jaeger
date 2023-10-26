from privytrace.helpers import CDR
import privytrace.groupsig as groupsig
import privytrace.trace_auth as trace_auth
import privytrace.traceback as traceback
from blspy import G1Element

tapk: G1Element = trace_auth.request_registration()
carriers = [1, 2, 3, 4, 5]
groups = {}

for carrier in carriers:
    groups[carrier] = groupsig.client_register(carrier)

callpath = [4, 3, 5, 1, 2]
src, dst = 1000, 1001


def trace():
    cdr = CDR(src=src, dst=dst, ts='2023-10-23 15:28:55', prev=1, curr=2 , next=None)
    records = traceback.trace(group=groups[2], tapk=tapk, cdrs=[cdr])
    print(records)
    
trace()

