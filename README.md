# fraud-graphing-neo4j
Understand fraud by finding shared attributes. Visualize connections in interactive graphs and query neo4j to find accounts sharing attributes.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed
- Python 3.8+ (for application code)

## Neo4j Setup

### 1. Configure Environment

Copy the example environment file and set your password:

```bash
cp .env.example .env
```

Edit `.env` and set a secure password:
```
NEO4J_PASSWORD=your_secure_password_here
```

### 2. Start Neo4j

```bash
docker compose up -d
```

### 3. Access Neo4j

- **Browser UI**: http://localhost:7474
- **Bolt Connection**: bolt://localhost:7687

Login with the credentials you set in `.env`.

### 4. Stop Neo4j

```bash
docker compose down
```

To also remove the data volumes:
```bash
docker compose down -v
```

## Connecting from Python

```python
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "your_password"))

with driver.session() as session:
    result = session.run("RETURN 'Hello, Neo4j!' AS message")
    print(result.single()["message"])

driver.close()
```

Install the Python driver:
```bash
pip install neo4j
```
