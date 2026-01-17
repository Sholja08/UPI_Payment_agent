

import json
import os
import random
from datetime import datetime, timedelta

# -----------------------------
# DB PATH (JSON)
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "transactions.json")

# -----------------------------
# GENERATE TRANSACTIONS
# -----------------------------
def generate_transactions(count=200):
    sender_banks = ["SBI", "HDFC", "ICICI", "AXIS", "PNB"]
    receiver_banks = ["SBI", "HDFC", "ICICI", "AXIS", "PNB"]
    statuses = ["SUCCESS", "FAILED", "PENDING"]

    transactions = []
    used_datetimes = set()  # ensure uniqueness

    for i in range(1, count + 1):
        txn_id = f"TXN{i:04d}"

        # 🔹 Random date within last 30 days
        random_days = random.randint(0, 30)
        base_date = datetime.now() - timedelta(days=random_days)

        # 🔹 Generate UNIQUE time
        while True:
            random_seconds = random.randint(0, 86399)  # seconds in a day
            dt = base_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            ) + timedelta(seconds=random_seconds)

            key = dt.strftime("%Y-%m-%d %H:%M:%S")
            if key not in used_datetimes:
                used_datetimes.add(key)
                break

        date = dt.strftime("%Y-%m-%d")
        time = dt.strftime("%H:%M:%S")

        amount = round(random.uniform(100, 5000), 2)
        sender_last4 = str(random.randint(1000, 9999))
        receiver_account_no = str(random.randint(7000000000, 9999999999))
        receiver_bank = random.choice(receiver_banks)
        sender_bank = random.choice(sender_banks)
        status = random.choice(statuses)

        description = (
            "Transaction completed successfully"
            if status == "SUCCESS"
            else "Transaction failed"
            if status == "FAILED"
            else "Transaction pending"
        )

        transaction = {
            "txn_id": txn_id,
            "date": date,
            "time": time,
            "amount": amount,
            "sender_last4": sender_last4,
            "receiver_account_no": receiver_account_no,
            "receiver_bank_name": receiver_bank,
            "sender_bank_name": sender_bank,
            "status": status,
            "description": description
        }

        transactions.append(transaction)

    return transactions

# -----------------------------
# SAVE TO JSON
# -----------------------------
def save_to_json(transactions):
    with open(JSON_PATH, "w") as f:
        json.dump(transactions, f, indent=4)
    print(f" {len(transactions)} transactions saved to {JSON_PATH}")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    transactions = generate_transactions(200)
    save_to_json(transactions)
    print(" transactions.json is ready for your payment agent!")



















