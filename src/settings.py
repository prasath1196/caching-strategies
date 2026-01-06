import sqlitecloud
import redis
import hashlib
import time
import dotenv
import os
dotenv.load_dotenv()

# --- 1. SETTINGS & SETUP (Simulating your settings.py) ---
def get_redis_client():
    r = redis.Redis(
        host=os.getenv("REDIS_URL"),
        port=os.getenv("REDIS_PORT"),
        decode_responses=True,
        username=os.getenv("REDIS_USERNAME"),
        password=os.getenv("REDIS_PASSWORD"),
    )
    return r

class SQLiteClient:
    def __init__(self):
        self.conn = sqlitecloud.connect(os.getenv("SQLLITE_URL"))
        self.create_table()

    def create_table(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)")
        # Seed some data if empty
        if not self.conn.execute("SELECT * FROM users WHERE id=1").fetchone():
            self.conn.execute("INSERT INTO users (id, username) VALUES (1, 'Alice')")
            self.conn.execute("INSERT INTO users (id, username) VALUES (2, 'Bob')")
            self.conn.commit()

    def execute(self, query, params=()):
        # SIMULATING DB LATENCY (The "Problem" with remote DBs)
        time.sleep(0.1) 
        cursor = self.conn.execute(query, params)
        self.conn.commit()
        return cursor

sqlite_client = SQLiteClient()