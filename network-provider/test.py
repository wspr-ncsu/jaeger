from models.helpers import CDR
import models.groupsig as groupsig
import models.trace_auth as trace_auth
import models.contribution as contribution
from blspy import G1Element

carrier_id: str = '1'
tapk: G1Element = trace_auth.register(carrier_id)
group: dict = groupsig.register(carrier_id)

cdr: CDR = CDR('1000', '1001', '2020-01-01 00:00:00', 1000, carrier_id, 3000)

contribution.contribute(group=group, tapk=tapk, cdrs=[cdr])

# print("Done!")