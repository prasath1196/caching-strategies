class LocalCache:
    def __init__(self, name):
        self.name = name 
        self.cache = {}

    def get(self, key):
        return self.cache.get(key) 
    
    def set(self, key, value):
        self.cache[key] = value 
    

    def flush(self):
        self.cache = {} 


# Assume there are two different cache nodes 

nodeA = LocalCache("nodeA")
nodeB = LocalCache("nodeB") 

# Let's put some data in NodeA and NodeB 
nodeA.set("name", "John")
nodeB.set("name", "John")


# Let's get the data from NodeA and NodeB 
# Let's get the data from NodeA and NodeB 
print(f"NodeA Initial: {nodeA.get('name')}") # John 
print(f"NodeB Initial: {nodeB.get('name')}") # John 
 

# Lets write update some data to NodeA 
print("\n--- Updating NodeA to 'Jane' ---")
nodeA.set("name", "Jane")

# Let's get the data from NodeA and NodeB 
print(f"NodeA Value: {nodeA.get('name')}") # Jane 
print(f"NodeB Value: {nodeB.get('name')} (!! STALE DATA !!)") # John => !! Stale Data !!


