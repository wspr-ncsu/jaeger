import random
import secrets
from . import redis
from . import response
from .config import WEKeys
from blspy import (BasicSchemeMPL, PrivateKey)

priv_id = 'TA.sk'
pubk_id = 'TA.pk'

def setup(refresh = False):
    # retrieve setup keys
    sk: str = None if refresh else redis.find(priv_id)
    pk: str = None if refresh else redis.find(pubk_id)
    
    if sk and pk:
        sk: PrivateKey = PrivateKey.from_bytes(bytes.fromhex(sk))
        return WEKeys(sk=sk, pk=pk)
    
    seed: bytes = bytes(secrets.token_bytes(32))
    sk: PrivateKey = BasicSchemeMPL.key_gen(seed)
    pk: str = bytes(sk.get_g1()).hex()
    
    redis.save(priv_id, bytes(sk).hex())
    redis.save(pubk_id, pk)
    
    return WEKeys(sk=sk, pk=pk)
    
 
def authorize(sk: PrivateKey, labels: list):
    sigs = {}
    
    for label in labels:
        msg = bytes(label, 'utf-8')
        sigma = BasicSchemeMPL.sign(sk, msg)
        sigs[label] = bytes(sigma).hex()
    
    return sigs