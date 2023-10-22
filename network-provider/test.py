from models.helpers import CDR
import models.groupsig as groupsig
import models.trace_auth as trace_auth
import models.contribution as contribution
import models.traceback as traceback
from datetime import datetime
from blspy import G1Element

tapk: G1Element = trace_auth.register()
carriers = [1, 2, 3, 4, 5]
groups = {}

for carrier in carriers:
    groups[carrier] = groupsig.register(carrier)

callpath = [4, 3, 5, 1, 2]
src, dst = 1000, 1001
ts = datetime.now()
cdrs = []

for index, curr in enumerate(callpath):
    prev = None if index == 0 else callpath[index - 1]
    next = None if index == len(callpath) - 1 else callpath[index + 1]
    # add random seconds to ts
    ts = ts.replace(second=ts.second + index)
    cdr = CDR(src=src, dst=dst, ts=ts.strftime('%Y-%m-%d %H:%M:%S'), prev=prev, curr=curr , next=next)
    
    contribution.contribute(group=groups[curr], tapk=tapk, cdrs=[cdr])


records = traceback.trace(group=groups['2'], tapk=tapk, cdrs=[cdr])
print(records)