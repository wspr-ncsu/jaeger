import os
import psycopg2
from json import loads
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from random import sample, randint


load_dotenv()

def env(envname, default=""):
    value = os.getenv(envname)
    return value or default

DB_HOST = env("DB_HOST")
DB_NAME = env("DB_NAME")
DB_PORT = env("DB_PORT")
DB_USER = env("DB_USER")
DB_PASS = env("DB_PASS")

def open_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

class CallRecord:
    def __init__(self, src, dst, next, prev) -> None:
        self.next = next
        self.prev = prev
        self.src = src
        self.dst = dst

class Provider:
    def __init__(self, id, name) -> None:
        self.id = id
        self.name = name
        
class Telco:
    def __init__(self, provider, cdr) -> None:
        self.provider = provider
        self.cdr = cdr
        
    def contribute(self):
        call_ts = round(datetime.now().timestamp())
        prev = next = None
        
        if self.cdr.prev is not None:
            prev = self.cdr.prev.id
            
        if self.cdr.next is not None:
            next = self.cdr.next.id
            
        cci = f"{self.cdr.src}:{self.cdr.dst}:{call_ts}"
        tbc = f"{prev}|{self.provider.id}|{cci}"
        tfc = f"{self.provider.id}|{next}|{cci}"
        
        opened_database = open_db()

        with opened_database.cursor() as cursor:
            query = f"INSERT INTO cdrs(cci,tbc,tfc) VALUES ('{cci}','{tbc}','{tfc}')"
            cursor.execute(query)
            
        opened_database.commit()
        opened_database.close()
        

class Faker:
    def __init__(self) -> None:
        pass
    
    def fake(self, number_of_calls_to_generate=2000):
        start_time = datetime.now().timestamp()
        counter = 1
        
        print('generating ' + str(number_of_calls_to_generate) + ' call(s)')

        try:
            # Read cached data from .json files
            stream = open(f'{Path.cwd()}/data/telcos.json')
            telcos = loads(stream.read())
            
            while counter <= number_of_calls_to_generate:
                # Get contributors. the +2 represents the originating and terminating service providers
                # For intermediate providers, we generate a random number between 1 and 5 inclusive
                contributors = sample(telcos, (randint(1, 3) + 1))
                
                src = randint(1000, 9999) # creating the originating number / caller
                dst = randint(1000, 9999) # creating the destination number / callee
                
                print(f"Simulating Call between {src} and {dst}")
                
                # For each contributor, create a doubly linked-list record (CallRecord instance) 
                # So that each provider knows the upstream and downstream providers
                for index, provider in enumerate(contributors):
                    prev = next = None
                    
                    if index > 0: 
                        contributor = contributors[index - 1]
                        prev = Provider(contributor.get('id'), contributor.get('name'))
                        
                    if index < len(contributors) - 1:
                        contributor = contributors[index + 1]
                        next = Provider(contributor.get('id'), contributor.get('name'))
                        
                    # Call record representing prev and next providers
                    cdr = CallRecord(src=src, dst=dst, next=next, prev=prev)
                    
                    # Current provider
                    provider = Provider(provider.get('id'), provider.get('name'))
                    
                    # Create the telco instance for that provider and contribute record to privyTrace server
                    current = Telco(provider, cdr)
                    current.contribute()
                    
                counter += 1
        except Exception as ex:
            print(ex)
            
        time_taken = datetime.now().timestamp() - start_time
        print("Time taken: " + str(time_taken))


if __name__ == '__main__':
    Faker().fake()