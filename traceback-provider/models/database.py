from redis import Redis
from .helpers import env
import clickhouse_connect
import json
import pathlib
from dotenv import load_dotenv

load_dotenv()

status_active = 1
status_inactive = 0
status_completed = 2

def open_db():
    DB_HOST = env("DB_HOST")
    DB_NAME = env("DB_NAME")
    DB_USER = env("DB_USER")
    DB_PASS = env("DB_PASS")
    
    return clickhouse_connect.get_client(
        host=DB_HOST, 
        username=DB_USER, 
        password=DB_PASS,
        database=DB_NAME
    )


def migrate():
    print('Starting Database Migrations')
    connection = open_db()
    
    text = pathlib.Path.cwd().joinpath('ddls.json').read_text()
    DDLs = json.loads(text)
    
    for ddl in DDLs:
        print("--> Running Migration: ", ddl)
        connection.command(DDLs[ddl])
        
    print('Migrations Completed.')
    
def insert_records(records, cols=['label', 'sigma', 'ct']):    
    connection = open_db()
    connection.insert("cdrs", data=records, column_names=cols)
    
def get_records(labels):
    connection = open_db()
    query = f"SELECT sigma, ct FROM cdrs WHERE label IN {labels}"
    result = connection.query(query)
    return result.result_rows
    