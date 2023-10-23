from os import getenv
from collections import namedtuple
from datetime import datetime

def write_to_file(filename, content):
    with open(filename, "w") as f:
        f.write(content)

def read_from_file(filename):
    with open(filename, "r") as f:
        return f.read()
    
def env(envname, default=""):
    value = getenv(envname)
    return value or default

def not_found():
    return { 'msg': 'The requested resource could not be found' }, 404
        
def toEpoch(date: str):
    if (type(date) is int):
        return date
    
    return int(datetime.strptime(date, '%Y-%m-%d %H:%M:%S').timestamp())
    
class Carrier:
    def __init__(self, group) -> None:
        pass

class CDR:
    label = None
    
    def __init__(self, src, dst, ts, prev, curr, next):
        self.src = src
        self.dst = dst
        self.ts = toEpoch(ts)
        self.prev = prev
        self.curr = curr
        self.next = next
        
    def get_call_detail(self):
        return f'{self.src}|{self.dst}|{self.ts}'
    
    def get_hops(self):
        return f'{self.prev}|{self.curr}|{self.next}'

