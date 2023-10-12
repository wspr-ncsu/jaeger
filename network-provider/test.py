from models.helpers import CDR
import models.groupsig as groupsig
import models.trace_auth as trace_auth
import models.contribution as contribution

cid = 2000
vk = trace_auth.register(cid)
gsign_keys = groupsig.register(cid)

# print("vk: ", vk)
print("gsign_keys: ", gsign_keys)
contribution.init(id=cid, gsign_keys=gsign_keys, vk=vk)

cdr = CDR('1000', '1001', '2020-01-01 00:00:00', 1000, cid, 2000)
res = contribution.contribute([cdr])
print(res)