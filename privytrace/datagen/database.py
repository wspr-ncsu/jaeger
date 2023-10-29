from redis import Redis
from .helpers import env
import clickhouse_connect
from .. import database as db

table = "raw_cdrs"

def save_cdrs(rows):
    columns = ["src", "dst", "ts", "prev", "curr", "next"]
    db.open_db().insert(table, data=rows, column_names=columns)