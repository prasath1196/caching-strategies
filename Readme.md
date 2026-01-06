# Distributed Caching Strategies Simulation

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Redis](https://img.shields.io/badge/Redis-Remote-red)
![SQLite](https://img.shields.io/badge/SQLite-Cloud-green)

A proof-of-concept project demonstrating core trade-offs in distributed systems and caching architectures. This project simulates and compares **Local Caching** (and its eventual consistency pitfalls) versus **Global Distributed Caching** (using consistent hashing and coordination patterns).

## 🚀 Key Distributed Systems Concepts

This project doesn't just use a cache; it simulates the architectural decisions required when scaling a system.

### 1. The "Stale Data" Problem (Local Caching)
*   **Concept**: `src/localcache.py` simulates multiple independent application nodes (`NodeA`, `NodeB`), each maintaining its own in-memory cache.
*   **Demonstration**:
    1.  Both nodes cache the value `User:1 -> "John"`.
    2.  `NodeA` updates `User:1` to `"Jane"`.
    3.  `NodeB` **remains stale**, serving `"John"` until its cache expires or is flushed.
*   **Takeaway**: Demonstrates why simple local caching fails in distributed environments requiring strong consistency.

### 2. The Global Coordinator Pattern
*   **Concept**: `src/globalcache.py` implements a centralized caching layer using **Redis** and a coordination logic.
*   **Architecture**:
    *   **Consistent Hashing / Sharding**: Keys are hashed to specific "Virtual Nodes" (`node_a`, `node_b`) represented by Redis key prefixes. This mimics how a load balancer or router would distribute traffic in a sharded cluster.
    *   **Read-Through Cache**:
        *   Request comes in -> Hash Key -> Find Node.
        *   Check Redis (Cache Impact).
        *   If Miss -> Read from SQLite (System of Record) -> Populate Redis -> Return.
    *   **Write-Through / Write-Aside**:
        *   Update Request -> Update SQLite (Durability).
        *   Update Redis immediately to ensure the next read is consistent.
*   **Takeaway**: Shows how to maintain consistency across a distributed data layer.

## 🛠️ Technology Stack

*   **Language**: Python 3.14
*   **Distributed Cache**: Redis (Cloud/Remote)
*   **Persistent Store**: SQLite Cloud (Simulating a scalable relational database)
*   **Environment**: Managed via `python-dotenv` for secure credential handling.

## ⚙️ Setup & Usage

### Prerequisites
*   Python 3.14+
*   Redis Cloud Instance (or local)
*   SQLite Cloud Account

### Installation

1.  **Clone the repository** and navigate to the project root.
2.  **Create a Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

Create a `.env` file in the root directory (see `.env.example`):

```bash
REDIS_URL='your-redis-host'
REDIS_PORT=12345
REDIS_USERNAME='default'
REDIS_PASSWORD='your-password'
SQLLITE_URL='sqlitecloud://your-project.sqlite.cloud:8860/dbname?apikey=your-api-key'
```

### Running the Simulators

**1. Test Local Caching Inconsistency:**
```bash
python src/localcache.py
```
> Observe how NodeA updates but NodeB serves old data.

**2. Test Global Caching Coordination:**
```bash
python src/globalcache.py
```
> Observe the Coordinator correctly routing requests and maintaining consistency between the DB and Cache.

---
<!-- *Built to demonstrate proficiency in Distributed Systems, Caching Strategies, and Python Software Engineering.* -->
