import random
from . import database as db
from witenc import bls, utils, encrypt, decrypt

signing_key = 'TA.sK'
verify_key = 'TA.vK'

def setup(refresh = False):
    db.connect()
    
    # retrieve setup keys
    sk = None if refresh else db.find(signing_key)
    vk = None if refresh else db.find(verify_key)
    
    if sk and vk:
        sk = utils.import_sk(sk)
        return sk, vk
    
    seed: bytes = bytes([random.randint(0, 255) for _ in range(32)])
    sk, vk = bls.key_gen(seed)
    vk = utils.export_pk(vk)
    db.save(signing_key, utils.export_sk(sk))
    db.save(verify_key, vk)
    
    return sk, vk
    
 
def sign(tag, sk):
    signature = bls.sign(sk, tag)
    return utils.export_sig(signature)