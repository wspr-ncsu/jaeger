import secrets
from . import redis
from .config import WEKeys, TA_pk_key, TA_sk_key
from witencpy import (Scheme, OTP, CipherText)
from blspy import (BasicSchemeMPL, PrivateKey, G1Element, G2Element)
import pickle

def server_setup(refresh = False):
    # retrieve setup keys
    sk: str = None if refresh else redis.find(TA_sk_key)
    pk: str = None if refresh else redis.find(TA_pk_key)
    
    if sk and pk:
        sk: PrivateKey = PrivateKey.from_bytes(bytes.fromhex(sk))
        return WEKeys(sk=sk, pk=pk)
    
    seed: bytes = bytes(secrets.token_bytes(32))
    sk: PrivateKey = BasicSchemeMPL.key_gen(seed)
    pk: str = bytes(sk.get_g1()).hex()
    
    redis.save(TA_sk_key, bytes(sk).hex())
    redis.save(TA_pk_key, pk)
    
    return WEKeys(sk=sk, pk=pk)
    
def server_authorize(sk: PrivateKey, labels: list):
    sigs = {}
    
    for label in labels:
        msg = bytes(label, 'utf-8')
        sigma = BasicSchemeMPL.sign(sk, msg)
        sigs[label] = bytes(sigma).hex()
    
    return sigs


# Client side functions

def client_encrypt(pk: G1Element, label: bytes, cdr: bytes) -> dict:
    key: bytes = bytes(BasicSchemeMPL.key_gen(secrets.token_bytes(32)))
    ct1: bytes = bytes(Scheme.encrypt(pk, label, key))
    ct2: bytes = bytes(OTP.encrypt(key, cdr))
    
    return { 'ct1': ct1, 'ct2': ct2 }

def client_decrypt(sig: G2Element, ct: dict) -> bytes:
    # Decrypt the key using witness encryption
    ct1: CipherText = CipherText.from_bytes(ct['ct1'])
    key: bytes = bytes(Scheme.decrypt(sig, ct1))
    
    # Decrypt the message with key using OTP
    msg = bytes(OTP.decrypt(key, ct['ct2']))
    
    return msg.decode()
    
def client_export_ct(ct: dict, dtype=str) -> str:
    ct: bytes = pickle.dumps(ct)
    
    if dtype == str:
        return ct.hex()
    
    return ct

def client_import_ct(ct: str) -> dict:
    if type(ct) == str:
        ct: bytes = bytes.fromhex(ct)
        
    return pickle.loads(ct)

def client_import_sig(sig: str) -> G2Element:
    if type(sig) == str:
        sig: bytes = bytes.fromhex(sig)
        
    return G2Element.from_bytes(sig)