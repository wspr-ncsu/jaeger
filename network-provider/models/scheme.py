from witencpy import (Scheme, OTP, CipherText)
from blspy import (BasicSchemeMPL, G1Element, G2Element)
import secrets
import pickle
from .helpers import CDR

pk: G1Element = None

def init(trace_auth_pub_key: G1Element):
    """Initialize the scheme with the given verification key"""
    global pk
    pk = trace_auth_pub_key

def encrypt(cdr: CDR) -> dict:
    # Generate a new key for each CDR
    key: bytes = bytes(BasicSchemeMPL.key_gen(secrets.token_bytes(32)))
    
    # We want to encrypt the key with witness encryption
    tag = bytes(f'{cdr.src}|{cdr.dst}|{cdr.ts}', 'utf-8')
    ct1: bytes = bytes(Scheme.encrypt(pk, tag, key))
    
    # We want to encrypt the message with the key using OTP
    msg: bytes = bytes(f'{cdr.prev}|{cdr.curr}|{cdr.next}', 'utf-8')
    ct2: bytes = bytes(OTP.encrypt(key, msg))
    
    return { 'ct1': ct1, 'ct2': ct2 }

def decrypt(sig: G2Element, ct: dict) -> bytes:
    # Decrypt the key using witness encryption
    ct1: CipherText = CipherText.from_bytes(ct.ct1)
    key: bytes = bytes(Scheme.decrypt(sig, ct1))
    
    # Decrypt the message with key using OTP
    msg = OTP.decrypt(key, ct.ct2)
    
    return msg
    
def export_ct(ct: dict, dtype=str) -> str:
    ct: bytes = pickle.dumps(ct)
    
    if dtype == str:
        return ct.hex()
    
    return ct

def import_ct(ct: str) -> dict:
    if type(ct) == str:
        ct: bytes = bytes.fromhex(ct)
        
    return pickle.loads(ct)