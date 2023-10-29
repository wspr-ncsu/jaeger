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
    res = db.open_db().query(f"SELECT src, dst, ts, prev, curr, next FROM {table} WHERE curr='{carrier}' and status=0")
    return res.result_rows

def mark_cdrs_as_contributed(carrier):
    db.open_db().command(f"ALTER TABLE {table} UPDATE status=1 WHERE curr='{carrier}'")