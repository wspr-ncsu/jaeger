from models.helpers import CDR
import models.groupsig as groupsig
import models.trace_auth as trace_auth
import models.contribution as contribution

cid = 2000
vk = trace_auth.register(cid)
mem_key, grp_key = groupsig.register(cid)

# print("vk: ", vk)
print("mem_key: ", mem_key)
print("grp_key: ", grp_key)
contribution.init(id=cid, mem_key=mem_key, grp_key=grp_key, vk=vk)

cdr = CDR('1000', '1001', '2020-01-01 00:00:00', 1000, cid, 2000)
res = contribution.contribute([cdr])
print(res)