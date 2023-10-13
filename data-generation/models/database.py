from redis import Redis
from .helpers import env
import clickhouse_connect
import json
import pathlib

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
    
def get_state():    
    connection = open_db()
    query = f"SELECT * FROM states WHERE status = {status_active}"
    result = connection.query(query).result_rows
    
    if len(result) == 0:
        return None
    
    return result[0]

def save_user_network(edges):
    connection = open_db()
    columns = ["id", "src", "dst"]
    rows = edges
    connection.insert("edges", data=rows, column_names=columns)
 
def clear_user_network():
    connection = open_db()
    connection.command("TRUNCATE TABLE edges")