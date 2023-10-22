from models.helpers import CDR
import models.groupsig as groupsig
import models.trace_auth as trace_auth
import models.contribution as contribution
from blspy import G1Element

carrier_id: str = '2000'
trace_auth_pub_key: G1Element = trace_auth.register(carrier_id)
group_signature_keys: dict = groupsig.register(carrier_id)

contribution.init(
    carrier_id=carrier_id, 
    trace_auth_pub_key=trace_auth_pub_key,
    group_signature_keys=group_signature_keys 
)

cdr: CDR = CDR('1000', '1001', '2020-01-01 00:00:00', 1000, carrier_id, 3000)

contribution.contribute([cdr])

print("Done!")