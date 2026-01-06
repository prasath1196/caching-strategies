import sqlite3
import redis
import hashlib
import time
import dotenv
dotenv.load_dotenv()

# --- 1. SETTINGS & SETUP (Simulating your settings.py) ---
def get_redis_client():
    return redis.Redis(host='localhost', port=6379, decode_responses=True)

class SQLiteClient:
    def __init__(self, db_name="app.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_table()

    def create_table(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        # Seed some data if empty
        if not self.conn.execute("SELECT * FROM users WHERE id=1").fetchone():
            self.conn.execute("INSERT INTO users (id, name) VALUES (1, 'Alice')")
            self.conn.execute("INSERT INTO users (id, name) VALUES (2, 'Bob')")
            self.conn.commit()

    def execute(self, query, params=()):
        # SIMULATING DB LATENCY (The "Problem" with remote DBs)
        time.sleep(0.1) 
        cursor = self.conn.execute(query, params)
        self.conn.commit()
        return cursor

sqlite_client = SQLiteClient()