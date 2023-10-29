from redis import Redis
from .helpers import env
import clickhouse_connect
from .. import database as db

table = "raw_cdrs"

def save_cdrs(rows):
    columns = ["src", "dst", "ts", "prev", "curr", "next"]
    db.open_db().insert(table, data=rows, column_names=columns)
    
def count_records():
    res = db.open_db().command(f"SELECT COUNT(*) FROM {table}")
    return res

def get_cdrs(carrier):
    res = db.open_db().query(f"SELECT * FROM {table} WHERE curr='{carrier}'")
    return res.result_rows

def clear_cdrs(carrier):
    db.open_db().command(f"DELETE FROM {table} WHERE curr='{carrier}'")