from witenc import bls, utils, encrypt, decrypt

vk = None

def init(k):
    """Initialize the scheme with the given verification key"""
    global vk
    vk = k

def encrypt():
    pass