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
ts = ['2023-10-23 15:28:51', '2023-10-23 15:28:53', '2023-10-23 15:28:53', '2023-10-23 15:28:54', '2023-10-23 15:28:55']
cdrs = []

def contribute():
    for index, curr in enumerate(callpath):
        prev = None if index == 0 else callpath[index - 1]
        next = None if index == len(callpath) - 1 else callpath[index + 1]
        cdr = CDR(src=src, dst=dst, ts=ts[index], prev=prev, curr=curr , next=next)
        contribution.contribute(group=groups[curr], tapk=tapk, cdrs=[cdr])
        cdrs.append(cdr)


def trace():
    cdr = CDR(src=src, dst=dst, ts='2023-10-23 15:28:55', prev=1, curr=2 , next=None)
    records = traceback.trace(group=groups[2], tapk=tapk, cdrs=[cdr])
    # print(records)
    
# contribute()
trace()

