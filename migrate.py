import argparse
from dotenv import load_dotenv
import jager.database as database

load_dotenv()

def main(args=None):
    database.migrate(DB_HOST='localhost')

if __name__ == '__main__':
    main()
