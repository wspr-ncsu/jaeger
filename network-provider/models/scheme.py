from witenc import bls, utils, encrypt as enc, decrypt as dec

vk = None

def init(k):
    """Initialize the scheme with the given verification key"""
    global vk
    vk = k

def encrypt(cdr):
    tag = f'{cdr.src}|{cdr.dst}|{cdr.ts}'
    message = f'{cdr.prev}|{cdr.curr}|{cdr.next}'
    return enc(pk=vk, tag=tag, message=message)