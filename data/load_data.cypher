// Load account data into Neo4j
// Run this after generating accounts.csv with seed_data.py

// Create constraints for unique identifiers
CREATE CONSTRAINT account_id_unique IF NOT EXISTS FOR (a:Account) REQUIRE a.account_id IS UNIQUE;
CREATE CONSTRAINT email_unique IF NOT EXISTS FOR (e:Email) REQUIRE e.address IS UNIQUE;
CREATE CONSTRAINT phone_unique IF NOT EXISTS FOR (p:Phone) REQUIRE p.number IS UNIQUE;

// Load accounts from CSV and create graph structure
// Accounts are nodes, Emails and Phones are shared nodes that accounts connect to
LOAD CSV WITH HEADERS FROM 'file:///accounts.csv' AS row

// Create or merge Account node
MERGE (a:Account {account_id: row.account_id})
SET a.first_name = row.first_name,
    a.last_name = row.last_name

// Create or merge Email node and relationship
MERGE (e:Email {address: row.email})
MERGE (a)-[:HAS_EMAIL]->(e)

// Create or merge Phone node and relationship
MERGE (p:Phone {number: row.phone})
MERGE (a)-[:HAS_PHONE]->(p);

// Create direct relationships between accounts that share attributes
MATCH (a:Account)-[:HAS_EMAIL]->(e:Email)<-[:HAS_EMAIL]-(b:Account)
WHERE a.account_id < b.account_id
MERGE (a)-[:SHARES_EMAIL {email: e.address}]->(b);

MATCH (a:Account)-[:HAS_PHONE]->(p:Phone)<-[:HAS_PHONE]-(b:Account)
WHERE a.account_id < b.account_id
MERGE (a)-[:SHARES_PHONE {phone: p.number}]->(b);

// Verify the data loaded correctly
// MATCH (a:Account) RETURN count(a) AS total_accounts;
// MATCH (e:Email)<-[:HAS_EMAIL]-(a:Account) WITH e, count(a) AS account_count WHERE account_count > 1 RETURN e.address, account_count ORDER BY account_count DESC;
// MATCH (p:Phone)<-[:HAS_PHONE]-(a:Account) WITH p, count(a) AS account_count WHERE account_count > 1 RETURN p.number, account_count ORDER BY account_count DESC;
