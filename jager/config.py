from os import getenv
from dotenv import load_dotenv
from collections import namedtuple
from pygroupsig import constants

load_dotenv()

def env(envname, default=""):
    value = getenv(envname)
    return value or default

APP_SECRET_KEY = env("APP_SECRET_KEY")

DB_HOST = env("DB_HOST")
DB_NAME = env("DB_NAME")
DB_USER = env("DB_USER")
DB_PASS = env("DB_PASS")

REDIS_HOST = env("REDIS_HOST")
REDIS_PORT = env("REDIS_PORT")
REDIS_PASS = env("REDIS_PASS")
REDIS_DB = env("REDIS_DB")

WEKeys = namedtuple('Keys', ['sk', 'pk'])
GSKeys = namedtuple('Keys', ['msk', 'gpk', 'gml'])

lh = 'http://127.0.0.1'

GS_Scheme = constants.BBS04_CODE
GM_HOST=env('GM_HOST', lh)
GM_PORT=9990
GM_MSK=env('GM_MSK')
GM_GPK=env('GM_GPK')
GM_GML=env('GM_GML')

LM_HOST=env('LM_HOST', lh)
LM_PORT=9991
LM_SK=env('LM_SK')

TA_HOST=env('TA_HOST', lh)
TA_PORT=9992
TA_PRIVK=env('TA_PRIVK')
TA_PUBK=env('TA_PUBK')

RS_HOST=env('RS_HOST', lh)
RS_PORT=9993

MAX_EPOCHS = 5 # Seconds

Carrier = namedtuple('Carrier', ['id', 'name', 'gsk'])
SIG_HEADER='X-Jager-Signature'

GM_BASE_URL = f'{GM_HOST}:{GM_PORT}'
LM_BASE_URL = f'{LM_HOST}:{LM_PORT}'
TA_BASE_URL = f'{TA_HOST}:{TA_PORT}'
ITG_BASE_URL = f'{RS_HOST}:{RS_PORT}'