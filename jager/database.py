import json
import pathlib
from . import config
import clickhouse_connect
from dotenv import load_dotenv

load_dotenv()

table = "ct_records"

def open_db():
    return clickhouse_connect.get_client(
        host=config.DB_HOST, 
        username=config.DB_USER, 
        password=config.DB_PASS,
        database=config.DB_NAME
    )


def migrate():
    print('Starting Database Migrations')
    connection = open_db()
    
    text = pathlib.Path.cwd().joinpath('schema.json').read_text()
    DDLs = json.loads(text)
    
    for ddl in DDLs:
        print("--> Running Migration: ", ddl)
        connection.command(DDLs[ddl])
        
    print('Migrations Completed.')
    
def insert_ct_records(records, cols=['label', 'sigma', 'ct']):    
    connection = open_db()
    connection.insert(table, data=records, column_names=cols)
    
def get_ciphertexts(labels):
    labels = '\',\''.join(labels)
    labels = f'\'{labels}\'' # wrap in quotes
    connection = open_db()
    query = f"SELECT label, sigma, ct FROM {table} WHERE label IN ({labels})"
    result = connection.query(query)
    
    cts = []
    
    for label, sigma, ct in result.result_rows:
        cts.append({ 'label': label, 'sigma': sigma, 'ct': ct })

    return cts

def get_registered_carriers():
    connection = open_db()
    query = f"SELECT id, name FROM carriers"
    return connection.query(query).result_rows

def get_carrier(cid):
    connection = open_db()
    query = f"SELECT id, name, gsk FROM carriers WHERE id={cid}"
    rows = connection.query(query).result_rows
    if len(rows) == 0:
        return None
    return config.Carrier(*rows[0])

def register_carrier(cid, name, gsk):
    insert_carriers([[cid, name, gsk]])
    
def insert_carriers(data):
    open_db().insert('carriers', data=data, column_names=['id', 'name', 'gsk'])