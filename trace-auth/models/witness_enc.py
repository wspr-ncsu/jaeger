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
    
 
def authorize(sk: PrivateKey, tag: bytes):
    if type(tag) is not bytes:
        raise Panic("Tag must be a bytes object")
    
    if not isinstance(sk, PrivateKey):
        raise Panic("Invalid signing key")
    
    signature = BasicSchemeMPL.sign(sk, tag)
    
    return bytes(signature).hex()