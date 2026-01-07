from globalcache import GlobalCache
from globalcache import Coordinator
from  settings import sqlite_client
import asyncio
import json

class WriteBackCoordinator(Coordinator):
    def __init__(self, global_cache, batch_size=3):
        super().__init__(global_cache)
        self.buffer = {}
        self.batch_size = batch_size
    
    def flush_buffer(self):
        print(f"   [Event-Based] Batch size {self.batch_size} reached! Flushing {len(self.buffer)} items...")
        for key, record in self.buffer.items():
            sqlite_client.execute("UPDATE users SET username = ? WHERE id = ?", (record['username'], key))
        self.buffer.clear()

    def update(self, key, value):
        # 1. Update Cache
        node_key = self._get_node_key(key) 
        record = {"id": key, "username": value}
        
        print(f"   [WriteBack] Buffer: {len(self.buffer)+1}/{self.batch_size} | Cache Update: {node_key}")
        self.cache.set(node_key, json.dumps(record))
        
        # 2. Add to Buffer
        self.buffer[key] = record
        
        # 3. Check Event (Batch Size)
        if len(self.buffer) >= self.batch_size:
            self.flush_buffer()


def main():
    print("\n" + "="*60)
    print("       EVENT-BASED WRITE-BACK (BATCH SIZE = 3)")
    print("="*60)
    
    # 0. RESET DB for Clean Demo
    print(" [0] RESETTING DB TO KNOWN STATE...")
    sqlite_client.execute("UPDATE users SET username='Alice' WHERE id=1")
    sqlite_client.execute("UPDATE users SET username='Bob' WHERE id=2")
    sqlite_client.execute("INSERT OR IGNORE INTO users (id, username) VALUES (3, 'Charlie')")

    wp = WriteBackCoordinator(GlobalCache(), batch_size=3)
    
    # 1. Initial State
    print("\n" + "-"*40)
    print(" [1] INITIAL STATE")
    print("-"*40)
    print(f" > App sees User 1: {wp.show(1)}") 

    # 2. Writes (Buffering Phase)
    print("\n" + "-"*40)
    print(" [2] FILLING BUFFER (Threshold=3)")
    print("-"*40)
    
    # Update 1
    print("\n >> Update 1: User 1 -> 'Alice_v1'")
    wp.update(1, "Alice_v1") 
    raw_db = sqlite_client.execute("SELECT username FROM users WHERE id = ?", (1,)).fetchone()[0]
    print(f"    [DB CHECK] User 1 is '{raw_db}' (STALE - Expected 'Alice_v1')")

    # Update 2
    print("\n >> Update 2: User 2 -> 'Bob_v1'")
    wp.update(2, "Bob_v1")
    raw_db = sqlite_client.execute("SELECT username FROM users WHERE id = ?", (2,)).fetchone()[0]
    print(f"    [DB CHECK] User 2 is '{raw_db}' (STALE - Expected 'Bob_v1')")

    # 3. Write 3 (Trigger Flush)
    print("\n" + "-"*40)
    print(" [3] TRIGGERING FLUSH (3rd Item)")
    print("-"*40)
    print(" >> Update 3: User 3 -> 'Charlie_v1'")
    
    # This will trigger the flush inside update()
    wp.update(3, "Charlie_v1") 

    # 4. Final Check
    print("\n" + "-"*40)
    print(" [4] EVENTUAL CONSISTENCY CHECK")
    print("-"*40)
    
    r1 = sqlite_client.execute("SELECT username FROM users WHERE id=1").fetchone()[0]
    r2 = sqlite_client.execute("SELECT username FROM users WHERE id=2").fetchone()[0]
    r3 = sqlite_client.execute("SELECT username FROM users WHERE id=3").fetchone()[0]
    
    print(f" > User 1 DB: '{r1}' (FRESH!)")
    print(f" > User 2 DB: '{r2}' (FRESH!)")
    print(f" > User 3 DB: '{r3}' (FRESH!)")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()