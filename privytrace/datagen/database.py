from redis import Redis
from .helpers import env
import clickhouse_connect
from .. import database as db

table = "raw_cdrs"

def get_subscriber_ids():
    res = db.open_db().query("SELECT id FROM subscribers")
    return res.result_rows

def update_subscriber_id(old_id, new_id):
    db.open_db().command(f"ALTER TABLE subscribers UPDATE edge_id='{new_id}' WHERE id='{old_id}'")

def save_subscribers(rows):
    columns = ["id", "phone", "carrier"]
    db.open_db().insert("subscribers", data=rows, column_names=columns)

def save_cdrs(rows):
    columns = ["src", "dst", "ts", "prev", "curr", "next"]
    db.open_db().insert(table, data=rows, column_names=columns)
    
def save_edges(rows):
    if len(rows) == 0:
        return
    columns = ["id", "src", "dst"]
    db.open_db().insert("edges", data=rows, column_names=columns)
    
def count_records():
    res = db.open_db().command(f"SELECT COUNT(*) FROM {table}")
    return res

def get_cdrs(carrier):
    res = db.open_db().query(f"SELECT src, dst, ts, prev, curr, next FROM {table} WHERE curr='{carrier}' and status=0")
    return res.result_rows

def mark_cdrs_as_contributed(carrier):
    db.open_db().command(f"ALTER TABLE {table} UPDATE status=1 WHERE curr='{carrier}'")
    
def truncate(tables: list):
    if type(tables) is not list:
        tables = [tables]
    
    for table in tables:
        db.open_db().command(f"TRUNCATE TABLE {table}")