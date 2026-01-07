import hashlib
import json
from settings import get_redis_client, sqlite_client

class GlobalCache:
    def __init__(self):
        self.r = get_redis_client()
        # We simulate "Nodes" using specific prefixes in the Global Redis
        self.nodes = ["node_a", "node_b", "node_c"]
        self.r.flushall()

class Coordinator:
    def __init__(self, global_cache):
        self.cache_system = global_cache
        self.cache = global_cache.r # Direct Redis access
        
    def _get_node_key(self, key):
        """
        Hashes the key to find the correct 'Virtual Node' prefix.
        This represents the Router sending traffic to a specific box.
        """
        # 1. Hashing
        hash_val = int(hashlib.md5(str(key).encode()).hexdigest(), 16)
        # 2. Modulo to pick a node
        node_index = hash_val % len(self.cache_system.nodes)
        node_prefix = self.cache_system.nodes[node_index]
        return f"{node_prefix}:{key}"

    def show(self, key):
        # 1. Calculate Route (Which node has this?)
        node_key = self._get_node_key(key)
        
        # 2. Check Cache
        print(f"[Coordinator] Checking {node_key}...")
        val = self.cache.get(node_key)
        
        if val:
            return f"[CACHE HIT] {json.loads(val)}"
        else:
            # 3. DB Fallback (Real SQLite Call)
            print("   [MISS] Reading from Real DB...")
            # Fetch Full Record
            row = sqlite_client.execute("SELECT * FROM users WHERE id = ?", (key,)).fetchone()
            
            if row:
                # Row is tuple (id, username)
                record = {"id": row[0], "username": row[1]}
                # 4. Populate Cache (Full Record)
                self.cache.set(node_key, json.dumps(record))
                return f"[DB READ] {record}"
            return None

    def update(self, key, value):
        print(f"\n--- UPDATE REQUEST: User {key} = {value} ---")
        
        # 1. UPDATE DB (The Source of Truth)
        # We do this first to ensure durability.
        print("   1. Writing to SQLite...")
        sqlite_client.execute("UPDATE users SET username = ? WHERE id = ?", (value, key))
        
        # 2. UPDATE CACHE
        # We must calculate the route again to find the correct node
        node_key = self._get_node_key(key)
        
        # Form Full Record
        record = {"id": key, "username": value}
        print(f"   2. Updating Cache Node ({node_key})...")
        self.cache.set(node_key, json.dumps(record))
      
    def flush(self):
        self.cache.flushall()

if __name__ == "__main__":
    global_cache = GlobalCache()
    coord = Coordinator(global_cache)

    # Scenario:
    # User 1 (Alice) is hashed to Node B (for example)
    # User 2 (Bob) is hashed to Node A

    print(coord.show(1)) # First Read (Miss -> DB -> Cache)
    print(coord.show(1)) # Second Read (Hit)

    # THE REAL UPDATE
    coord.update(1, "Alice_Updated")

    # Verify Consistency
    print(coord.show(1)) # Should return "Alice_Updated" from Cache