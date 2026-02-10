"""
Generate dummy account data with fraud patterns for Neo4j.

Fraud patterns:
- 20 accounts share the same email address (different names/account IDs)
- 15 of those 20 also share the same phone number
- 5 additional accounts (not in the email group) share a different phone number
- 75 accounts are "normal" with unique emails and phones
"""

import csv
import random
import string
from pathlib import Path

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna", "Stephen", "Brenda", "Amos"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Johnson"
]

DOMAINS = ["fakemail.test", "notreal.example", "testbox.invalid", "mockmail.test", "sample.example"]


def generate_account_id():
    return "ACC" + "".join(random.choices(string.digits, k=8))


def generate_email(first_name, last_name):
    patterns = [
        f"{first_name.lower()}.{last_name.lower()}",
        f"{first_name.lower()}{last_name.lower()}",
        f"{first_name[0].lower()}{last_name.lower()}",
        f"{first_name.lower()}{random.randint(1, 99)}",
    ]
    return f"{random.choice(patterns)}@{random.choice(DOMAINS)}"


def generate_phone():
    exchange = random.randint(200, 999)
    subscriber = random.randint(1000, 9999)
    return f"555-{exchange}-{subscriber}"


def generate_name():
    return random.choice(FIRST_NAMES), random.choice(LAST_NAMES)


def main():
    accounts = []
    used_account_ids = set()

    def unique_account_id():
        while True:
            acc_id = generate_account_id()
            if acc_id not in used_account_ids:
                used_account_ids.add(acc_id)
                return acc_id

    # Shared fraud indicators
    shared_email_1 = "suspicious.user@fakemail.test"
    shared_email_2 = "fraud.ring@notreal.example"
    shared_phone_1 = "555-123-4567"  # Used by 15 of the 20 email-sharing accounts
    shared_phone_2 = "555-987-6543"  # Used by 5 separate accounts

    # Group 1: 20 accounts sharing the same email (shared_email_1)
    # 15 of these also share phone_1, 5 have unique phones
    for i in range(20):
        first_name, last_name = generate_name()
        if i < 15:
            phone = shared_phone_1
        else:
            phone = generate_phone()

        accounts.append({
            "account_id": unique_account_id(),
            "first_name": first_name,
            "last_name": last_name,
            "email": shared_email_1,
            "phone": phone,
        })

    # Group 2: 8 accounts sharing a second email (shared_email_2)
    for _ in range(8):
        first_name, last_name = generate_name()
        accounts.append({
            "account_id": unique_account_id(),
            "first_name": first_name,
            "last_name": last_name,
            "email": shared_email_2,
            "phone": generate_phone(),
        })

    # Group 3: 5 accounts sharing phone_2 (different email each)
    for _ in range(5):
        first_name, last_name = generate_name()
        accounts.append({
            "account_id": unique_account_id(),
            "first_name": first_name,
            "last_name": last_name,
            "email": generate_email(first_name, last_name),
            "phone": shared_phone_2,
        })

    # Group 4: 67 normal accounts (unique emails and phones)
    for _ in range(67):
        first_name, last_name = generate_name()
        accounts.append({
            "account_id": unique_account_id(),
            "first_name": first_name,
            "last_name": last_name,
            "email": generate_email(first_name, last_name),
            "phone": generate_phone(),
        })

    # Shuffle to mix fraud accounts with normal ones
    random.shuffle(accounts)

    # Write to CSV
    output_path = Path(__file__).parent / "accounts.csv"
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["account_id", "first_name", "last_name", "email", "phone"]
        )
        writer.writeheader()
        writer.writerows(accounts)

    print(f"Generated {len(accounts)} accounts to {output_path}")
    print(f"  - 20 accounts share email: {shared_email_1}")
    print(f"  - 15 of those also share phone: {shared_phone_1}")
    print(f"  - 8 accounts share email: {shared_email_2}")
    print(f"  - 5 separate accounts share phone: {shared_phone_2}")
    print(f"  - 67 normal accounts with unique emails/phones")


if __name__ == "__main__":
    main()
