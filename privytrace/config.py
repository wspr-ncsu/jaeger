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

GS_Scheme = constants.BBS04_CODE
GS_gpk_key = 'GM.gpk'
GS_msk_key = 'GM.msk'
GS_gml_key = 'GM.gml'

TA_sk_key = 'TA.sk'
TA_pk_key = 'TA.pk'

LM_sk_key = 'LM.sk'

GM_BASE_URL = env('GM_BASE_URL', 'http://localhost:9990')
LM_BASE_URL = env('LM_BASE_URL', 'http://localhost:9991')
TA_BASE_URL = env('TA_BASE_URL', 'http://localhost:9992')
ITG_BASE_URL = env('ITG_BASE_URL', 'http://localhost:9993')

MAX_EPOCHS = 5 # Seconds