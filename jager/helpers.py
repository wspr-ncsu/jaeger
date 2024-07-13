import time
import json
import secrets
import os
from .response import Panic
from datetime import datetime
import logging

logger = logging.getLogger('jager')
logger.setLevel(logging.DEBUG)

# Create a console handler and set the level to debug
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

def write_to_file(filename, content):
    with open(filename, "w") as f:
        f.write(content)

def read_from_file(filename):
    with open(filename, "r") as f:
        return f.read()
        
def validate_cid(cid):
    if not cid:
        raise Panic("Missing cid")
    
    cid = int(cid)
    
    if cid < 1 or cid > 7000:
        raise Panic("Unrecognized ID")
    
    return cid

def validate_json_list(payload):
    if not payload:
        raise Panic("Missing payload")
    
    payload = json.loads(payload)
    
    if not isinstance(payload, list):
        raise Panic("xs must be a list")

    return payload

def validate_json(payload):
    if not payload:
        raise Panic("Missing payload")
    
    payload = json.loads(payload)
    
    if not isinstance(payload, dict):
        raise Panic("xs must be a dict")

    return payload

def toEpoch(date: str):
    if (type(date) is int):
        return date
    
    if date.isnumeric():
        return int(date)
    
    return int(datetime.strptime(date, '%Y-%m-%d %H:%M:%S').timestamp())

class CDR:
    label = None
    
    def __init__(self, src, dst, ts, prev = None, curr = None, next = None):
        # self.id = id
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
    
    
def startStopwatch():
    return time.perf_counter()

def endStopwatch(test_name, start, numIters, silent=False):
    end_time = time.perf_counter()
    total_dur_ms = (end_time - start) * 1000
    avg_dur_ms = total_dur_ms / numIters

    if not silent:
        print("\n%s\nTotal: %d runs in %0.1f ms\nAvg: %fms"
            % (test_name, numIters, total_dur_ms, avg_dur_ms))
        
    return test_name, total_dur_ms, avg_dur_ms
    
def random_bytes(n, hex=False):
    d = secrets.token_bytes(n)
    if hex:
        return d.hex()
    return d

def update_csv(file, line, header = None):
    with open(f'results/{file}', 'a') as f:
        # Write header if file is empty
        if f.tell() == 0 and header:
            f.write(header + '\n')
            
        f.write(line + '\n')
        
def create_csv(file, header, mode = 'a'):
    with open(f'results/{file}', mode) as f:
        if f.tell() == 0:
            f.write(header + '\n')

def create_folder_if_not_exists(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)