import random
import secrets
from . import database as db
from blspy import (BasicSchemeMPL, PrivateKey)
from .helpers import Keys, Panic

priv_id = 'TA.sk'
pubk_id = 'TA.pk'

def setup(refresh = False):
    db.connect()
    
    # retrieve setup keys
    sk: str = None if refresh else db.find(priv_id)
    pk: str = None if refresh else db.find(pubk_id)
    
    if sk and pk:
        sk: PrivateKey = PrivateKey.from_bytes(bytes.fromhex(sk))
        return Keys(sk=sk, pk=pk)
    
    seed: bytes = bytes(secrets.token_bytes(32))
    sk: PrivateKey = BasicSchemeMPL.key_gen(seed)
    pk: str = bytes(sk.get_g1()).hex()
    
    db.save(priv_id, bytes(sk).hex())
    db.save(pubk_id, pk)
    
    return Keys(sk=sk, pk=pk)
    
 
def authorize(sk: PrivateKey, labels: list):
    sigs = {}
    
    for label in labels:
        msg = bytes(label, 'utf-8')
        sigma = BasicSchemeMPL.sign(sk, msg)
        sigs[label] = bytes(sigma).hex()
    
    return sigs