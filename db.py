import psycopg2
from config import Config


class ConnectToDB:
    def __init__(self):
        config = Config()
        self.dbname = config.db_name
        self.db_host = config.db_host
        self.db_user = config.db_user
        self.db_pass = config.db_pass

    def __enter__(self):
        dsn = f"dbname={self.dbname} host={self.db_host} user={self.db_user} password={self.db_pass}"
        self.db = psycopg2.connect(dsn)
        self.cur = self.db.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.db.close()
