from dotenv import load_dotenv
import jager.database as database

load_dotenv()

if __name__ == '__main__':
    database.migrate()
