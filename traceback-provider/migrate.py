import models.database as database
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    database.migrate()
