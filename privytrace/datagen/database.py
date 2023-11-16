from redis import Redis
from .helpers import env
import clickhouse_connect
import math
from .. import database as db
from ..helpers import random_bytes

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
    db.open_db().insert("raw_cdrs", data=rows, column_names=columns)
    
def save_edges(rows):
    if len(rows) == 0:
        return
    columns = ["id", "src", "dst"]
    db.open_db().insert("edges", data=rows, column_names=columns)
    
def count_records():
    res = db.open_db().command(f"SELECT COUNT(*) FROM raw_cdrs")
    return res

def get_cdrs(num_records, status=0):
    query = f"SELECT id, src, dst, ts, prev, curr, next FROM raw_cdrs WHERE status={status} LIMIT {num_records}"
    res = db.open_db().query(query)
    return res.result_rows

def mark_cdrs_as_contributed(ids):
    db.open_db().command(f"ALTER TABLE raw_cdrs UPDATE status=1 WHERE id in ('{ids}')")
    
def truncate(tables: list):
    if type(tables) is not list:
        tables = [tables]
    
    for table in tables:
        db.open_db().command(f"TRUNCATE TABLE {table}")
        
def get_all_edges():
    res = db.open_db().query(
        f"SELECT S.phone AS src, D.phone AS dst FROM edges E JOIN subscribers S ON E.src = S.id JOIN subscribers D ON E.dst = D.id ORDER BY E.id ASC"
    )
    return res.result_rows

def get_number_of_pages_in_edges(per_page):
    total = db.open_db().command(f"SELECT COUNT(*) FROM edges")
    return math.ceil(total / per_page)

def records_exists():
    edges = db.open_db().command(f"SELECT COUNT(*) FROM edges")
    subs = db.open_db().command(f"SELECT COUNT(*) FROM subscribers")
    return edges > 0 and subs > 0

def find_ct_records_by_random_label():
    labels = "','".join([ random_bytes(32).hex() for _ in range(10) ])
    res = db.open_db().query(f"SELECT * FROM ct_records WHERE label  in ('{labels}')")
    return res.result_rows

def get_table_sizes():
    query = """
        SELECT table, formatReadableSize(size) as size, rows, days, formatReadableSize(avgDaySize) as avgDaySize FROM (
            SELECT
                table,
                sum(bytes) AS size,
                sum(rows) AS rows,
                min(min_date) AS min_date,
                max(max_date) AS max_date,
                (max_date - min_date) AS days,
                size / (max_date - min_date) AS avgDaySize
            FROM system.parts
            WHERE active
            GROUP BY table
            ORDER BY rows DESC
        )
    """
    result = db.open_db().query(query)
    return result.result_rows