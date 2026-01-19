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

## Loading Sample Data

The `data/` directory contains sample fraud data with 100 accounts:
- **20 accounts** share the same email address (`suspicious.user@fakemail.test`)
- **15 of those** also share the same phone number (`555-123-4567`)
- **5 additional accounts** share a different phone number (`555-987-6543`)
- **75 accounts** are "normal" with unique emails and phones

### Generate and Load Data

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Generate the CSV data:
```bash
python data/seed_data.py
```

3. Start Neo4j (if not running):
```bash
docker compose up -d
```

4. Load the data into Neo4j:
```bash
python load_database.py
```

### Useful Queries

Find accounts sharing an email:
```cypher
MATCH (e:Email)<-[:HAS_EMAIL]-(a:Account)
WITH e, collect(a) AS accounts
WHERE size(accounts) > 1
RETURN e.address AS email, size(accounts) AS account_count, accounts
```

Find accounts sharing a phone:
```cypher
MATCH (p:Phone)<-[:HAS_PHONE]-(a:Account)
WITH p, collect(a) AS accounts
WHERE size(accounts) > 1
RETURN p.number AS phone, size(accounts) AS account_count, accounts
```

Visualize fraud network (accounts sharing email AND phone):
```cypher
MATCH (a:Account)-[:HAS_EMAIL]->(e:Email)<-[:HAS_EMAIL]-(b:Account)
WHERE a <> b
MATCH (a)-[:HAS_PHONE]->(p:Phone)<-[:HAS_PHONE]-(b)
RETURN a, b, e, p
```
