import sys
from json import loads
from pathlib import Path
from datetime import datetime
from random import sample, randint, choice
import requests

tracing_url = 'http://127.0.0.1:5000/tracer'
contribution_url = 'http://127.0.0.1:5000/contribute'
        
class CallRecord:
    def __init__(self, src, dst, ts, next, prev) -> None:
        self.next = next
        self.prev = prev
        self.src = src
        self.dst = dst
        self.ts = ts

class Provider:
    def __init__(self, id, name) -> None:
        self.id = id
        self.name = name
        
class Telco:
    def __init__(self, provider, cdr) -> None:
        self.cdr = cdr
        self.provider = provider
        
    def contribute(self):
        prev = next = None
        
        if self.cdr.prev is not None:
            prev = self.cdr.prev.id
            
        if self.cdr.next is not None:
            next = self.cdr.next.id
            
        cci = f"{self.cdr.src}:{self.cdr.dst}:{self.cdr.ts}"
        tbc = f"{prev}|{self.provider.id}|{cci}"
        tfc = f"{self.provider.id}|{next}|{cci}"
        
        # make request to backend to submit cci, tbc, and tfc
        payload = { 'cci': cci, 'tbc': tbc, 'tfc': tfc }
        
        response = requests.post(contribution_url, payload)
        
        if response.ok:
            return f"{self.provider.id}\n\ttbc\t=\t{tbc}\n\ttfc\t=\t{tfc}"
        else:
            return f"{self.provider.id} failed to submit record"
        
class Demo:
    def __init__(self) -> None:
        pass
    
    def run(self, number_of_calls_to_generate=20):
        counter = 1

        try:
            stream = open(f'{Path.cwd()}/data/demo.json')
            telcos = loads(stream.read())
            
            while counter <= number_of_calls_to_generate:
                contributors = sample(telcos, randint(2, 6))
                
                originator = contributors[0]
                terminator = contributors[-1]
                
                src = choice(originator.get('subscribers'))
                dst = choice(terminator.get('subscribers'))
                
                print(f"Intiated call from {src} ({originator.get('id')}) to {dst} ({terminator.get('name')})")
                
                call_path = []
                ts = round(datetime.now().timestamp())
                
                contribution_log = []
                
                for index, provider in enumerate(contributors):
                    call_path.append(provider.get('id'))
                    
                    prev = next = None
                    
                    if index > 0: 
                        contributor = contributors[index - 1]
                        prev = Provider(contributor.get('id'), contributor.get('name'))
                        
                    if index < len(contributors) - 1:
                        contributor = contributors[index + 1]
                        next = Provider(contributor.get('id'), contributor.get('name'))
                        
                    # Call record representing prev and next providers
                    cdr = CallRecord(src=src, dst=dst, ts=ts, next=next, prev=prev)
                    
                    # Current provider
                    provider = Provider(provider.get('id'), provider.get('name'))
                    
                    # Create the telco instance for that provider and contribute record to privyTrace server
                    current = Telco(provider, cdr)
                    contribution_log.append(current.contribute())
                    
                contribution_log = "\n".join(contribution_log)
                log = f"src_tn\t=\t{src} ({originator.get('id')})\ndst_tn\t=\t{dst} ({terminator.get('id')})\ncall_ts\t=\t{ts}\nhops\t=\t{' -> '.join(call_path)}\n{contribution_log}\n{'=' * 100}"
                
                print(log, file=sys.stderr) # stderr will send to demo.log file
                print('')
                
                counter += 1
        except Exception as ex:
            print(ex.with_traceback())
            
            
class Tracer:
    def __init__(self, type, param) -> None:
        key = ''
        if type == 'traceback':
            key = 'tbc'
        elif type == 'traceforward': 
            key = 'tfc'
        else:
            key = 'cci'
            
        self.payload = { 'type': type, key: param }
    
    def run(self):
        response = requests.post(tracing_url, self.payload)
        result = response.json()
        print("\nResult Set:")
        
        path = []
        
        last_item_index = len(result) - 1
        
        for index, item in enumerate(result):
            print(f"\t{item}")
            parts = item.split('|')
            curr = ""
            if self.payload['type'] == 'traceback':
                curr = parts[1]
            elif self.payload['type'] == 'traceforward':
                curr = parts[0]
            else:
                if index == last_item_index:
                    curr = parts[0]
                else:
                    curr = parts[1]
                
            path.append(curr)
        
        if self.payload['type'] != 'lookup':
            print(f"\n{self.payload['type']}\t=\t{' -> '.join(path)}\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('PLEASE PROVIDE COMMAND')
        
    command = sys.argv[1]
    
    if command == 'run':
        Demo().run()
    elif command in ['traceback', 'traceforward', 'lookup']:
        Tracer(command, sys.argv[2]).run()
    else:
        print('Uknown command.\nValid:(run, tracer)')