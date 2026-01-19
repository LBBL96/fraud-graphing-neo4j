"""
Load account data from CSV into Neo4j database.

Usage:
    python load_database.py

Requires:
    pip install neo4j
"""

import csv
import os
from pathlib import Path

from neo4j import GraphDatabase


def get_driver():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    return GraphDatabase.driver(uri, auth=(username, password))


def clear_database(session):
    """Remove all nodes and relationships."""
    session.run("MATCH (n) DETACH DELETE n")
    print("Cleared existing data")


def create_constraints(session):
    """Create uniqueness constraints."""
    constraints = [
        "CREATE CONSTRAINT account_id_unique IF NOT EXISTS FOR (a:Account) REQUIRE a.account_id IS UNIQUE",
        "CREATE CONSTRAINT email_unique IF NOT EXISTS FOR (e:Email) REQUIRE e.address IS UNIQUE",
        "CREATE CONSTRAINT phone_unique IF NOT EXISTS FOR (p:Phone) REQUIRE p.number IS UNIQUE",
    ]
    for constraint in constraints:
        session.run(constraint)
    print("Created constraints")


def load_accounts(session, csv_path):
    """Load accounts from CSV and create graph structure."""
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        accounts = list(reader)

    for account in accounts:
        session.run(
            """
            MERGE (a:Account {account_id: $account_id})
            SET a.first_name = $first_name, a.last_name = $last_name
            MERGE (e:Email {address: $email})
            MERGE (a)-[:HAS_EMAIL]->(e)
            MERGE (p:Phone {number: $phone})
            MERGE (a)-[:HAS_PHONE]->(p)
            """,
            account_id=account["account_id"],
            first_name=account["first_name"],
            last_name=account["last_name"],
            email=account["email"],
            phone=account["phone"],
        )

    print(f"Loaded {len(accounts)} accounts")


def create_shared_relationships(session):
    """Create SHARES_EMAIL and SHARES_PHONE relationships between accounts."""
    session.run(
        """
        MATCH (a:Account)-[:HAS_EMAIL]->(e:Email)<-[:HAS_EMAIL]-(b:Account)
        WHERE a.account_id < b.account_id
        MERGE (a)-[:SHARES_EMAIL {email: e.address}]->(b)
        """
    )

    session.run(
        """
        MATCH (a:Account)-[:HAS_PHONE]->(p:Phone)<-[:HAS_PHONE]-(b:Account)
        WHERE a.account_id < b.account_id
        MERGE (a)-[:SHARES_PHONE {phone: p.number}]->(b)
        """
    )

    print("Created SHARES_EMAIL and SHARES_PHONE relationships")


def print_summary(session):
    """Print summary of loaded data."""
    result = session.run("MATCH (a:Account) RETURN count(a) AS count")
    account_count = result.single()["count"]

    result = session.run(
        """
        MATCH (e:Email)<-[:HAS_EMAIL]-(a:Account)
        WITH e, count(a) AS cnt WHERE cnt > 1
        RETURN e.address AS email, cnt
        ORDER BY cnt DESC
        """
    )
    shared_emails = list(result)

    result = session.run(
        """
        MATCH (p:Phone)<-[:HAS_PHONE]-(a:Account)
        WITH p, count(a) AS cnt WHERE cnt > 1
        RETURN p.number AS phone, cnt
        ORDER BY cnt DESC
        """
    )
    shared_phones = list(result)

    print(f"\nSummary:")
    print(f"  Total accounts: {account_count}")
    print(f"  Shared emails: {len(shared_emails)}")
    for record in shared_emails:
        print(f"    - {record['email']}: {record['cnt']} accounts")
    print(f"  Shared phones: {len(shared_phones)}")
    for record in shared_phones:
        print(f"    - {record['phone']}: {record['cnt']} accounts")


def main():
    csv_path = Path(__file__).parent / "data" / "accounts.csv"

    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}")
        print("Run 'python data/seed_data.py' first to generate the data.")
        return

    driver = get_driver()

    try:
        with driver.session() as session:
            clear_database(session)
            create_constraints(session)
            load_accounts(session, csv_path)
            create_shared_relationships(session)
            print_summary(session)
    finally:
        driver.close()

    print("\nDone! View the graph at http://localhost:7474")


if __name__ == "__main__":
    main()
