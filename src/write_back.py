from globalcache import GlobalCache
from globalcache import Coordinator
from  settings import sqlite_client
import asyncio
import json

class WriteBackCoordinator(Coordinator):
    def __init__(self, global_cache):
        super().__init__(global_cache)
        # Buffer stores {user_id: {"id": user_id, "username": "Alice..."}}
        self.buffer = {}
    
    async def perform_write(self):
        print("   [Background] Writer sleeping for 2s...")
        await asyncio.sleep(2)
        print(f"   [Background] Flushing {len(self.buffer)} items to DB...")
        for key, record in self.buffer.items():
            # Extract 'username' from the record for the SQL update
            sqlite_client.execute("UPDATE users SET username = ? WHERE id = ?", (record['username'], key))
        self.buffer.clear()

    async def update(self, key, value):
        # FIX 1: Do NOT call super().update()
        
        node_key = self._get_node_key(key) 
        
        # Construct the FULL RECORD to cache
        record = {"id": key, "username": value}
        
        print(f"   [WriteBack] Updating Cache Node ({node_key})...")
        # Cache as JSON
        self.cache.set(node_key, json.dumps(record))
        
        # Buffer the FULL RECORD
        self.buffer[key] = record
        
        asyncio.create_task(self.perform_write())


async def main():
    print("\n" + "="*60)
    print("       WRITE-BACK POLICY SIMULATION")
    print("="*60)
    
    wp = WriteBackCoordinator(GlobalCache())
    
    # 1. Initial State
    print("\n" + "-"*40)
    print(" [1] INITIAL STATE")
    print("     (Fetching User 1 - Should come from DB)")
    print("-"*40)
    print(f" > App sees: {wp.show(1)}") 

    # 2. Perform Write
    print("\n" + "-"*40)
    print(" [2] WRITING DATA (Write-Back)")
    print("     (Updates Cache ONLY, Buffers DB write)")
    print("-"*40)
    await wp.update(1, "Alice_Updated_WriteBack")
    
    # 3. Prove Inconsistency
    print("\n" + "-"*40)
    print(" [3] IMMEDIATE FETCH & INCONSISTENCY CHECK")
    print("     (App should see fresh cache, DB should be stale)")
    print("-"*40)
    print(f" > App sees: {wp.show(1)}") 
    
    raw_db = sqlite_client.execute("SELECT username FROM users WHERE id = ?", (1,)).fetchone()[0]
    print(f" > DB holds: '{raw_db}' (STALE!)")

    # 4. Background Flush
    print("\n" + "-"*40)
    print(" [4] BACKGROUND SYNCHRONIZATION")
    print("     (Waiting for async writer to flush buffer...)")
    print("-"*40)
    await asyncio.sleep(3) 

    # 5. Final Check
    print("\n" + "-"*40)
    print(" [5] EVENTUAL CONSISTENCY CHECK")
    print("     (DB should now match Cache)")
    print("-"*40)
    raw_db_final = sqlite_client.execute("SELECT username FROM users WHERE id = ?", (1,)).fetchone()[0]
    print(f" > DB holds: '{raw_db_final}' (FRESH!)")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())