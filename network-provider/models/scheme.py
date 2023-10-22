from witencpy import (Scheme, OTP, CipherText)
from blspy import (BasicSchemeMPL, G1Element, G2Element)
import secrets
import pickle
from .helpers import CDR

def encrypt(pk: G1Element, label: bytes, cdr: bytes) -> dict:
    key: bytes = bytes(BasicSchemeMPL.key_gen(secrets.token_bytes(32)))
    ct1: bytes = bytes(Scheme.encrypt(pk, label, key))
    ct2: bytes = bytes(OTP.encrypt(key, cdr))
    
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

def import_sig(sig: str) -> G2Element:
    if type(sig) == str:
        sig: bytes = bytes.fromhex(sig)
        
    return G2Element.from_bytes(sig)