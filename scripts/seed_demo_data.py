import asyncio
import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, text
from backend.app.db.session import async_session_maker
from backend.app.db.models.account import Account
from backend.app.db.models.transaction import Transaction
from backend.app.db.models.alert import Alert

# Indian context names and types
TX_TYPES = ["UPI", "NEFT", "IMPS", "RTGS"]
LOCATIONS = ["Mumbai, IN", "Delhi, IN", "Bangalore, IN", "Hyderabad, IN", "Chennai, IN", "Kolkata, IN", "Pune, IN"]
FIRST_NAMES = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Riya", "Diya", "Saanvi", "Aanya", "Kavya"]
LAST_NAMES = ["Sharma", "Patel", "Singh", "Kumar", "Das", "Reddy", "Gupta", "Joshi", "Menon", "Bose"]

def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

async def seed_data():
    print("Seeding database...")
    async with async_session_maker() as session:
        # Clean up previous seed data (order matters for FK constraints)
        print("Cleaning old seed data...")
        await session.execute(delete(Alert))
        await session.execute(text("DELETE FROM model_predictions"))
        await session.execute(delete(Transaction))
        await session.execute(delete(Account))
        await session.commit()
        print("Old data cleared.")
        # Generate 100 random accounts
        accounts = []
        for i in range(100):
            acc_id = f"ACC_{i:04d}"
            acc = Account(
                id=acc_id,
                account_number=f"0000{random.randint(100000, 999999)}",
                customer_name=random_name(),
                risk_score=random.uniform(0.01, 0.2),
                anomaly_score=random.uniform(0.01, 0.1),
                graph_score=0.0,
                is_frozen=False
            )
            accounts.append(acc)
            session.add(acc)
        
        # 5 Mule Accounts
        mule_accounts = []
        for i in range(5):
            acc_id = f"MULE_{i:04d}"
            acc = Account(
                id=acc_id,
                account_number=f"9999{random.randint(100000, 999999)}",
                customer_name=random_name(),
                risk_score=random.uniform(0.8, 0.99),
                anomaly_score=random.uniform(0.7, 0.9),
                graph_score=0.95,
                is_frozen=True
            )
            mule_accounts.append(acc)
            session.add(acc)
            
        await session.commit()
        print("Inserted Accounts.")

        # 200 Legitimate Transactions
        normal_txs = []
        for i in range(200):
            sender = random.choice(accounts)
            receiver = random.choice(accounts)
            while receiver.id == sender.id:
                receiver = random.choice(accounts)
            
            tx_id = str(uuid.uuid4())
            amount = round(random.uniform(100.0, 50000.0), 2)
            score = random.uniform(0.01, 0.3)
            
            tx = Transaction(
                id=tx_id,
                sender_account_id=sender.id,
                receiver_account_id=receiver.id,
                amount=amount,
                transaction_type=random.choice(TX_TYPES),
                geo_location=random.choice(LOCATIONS),
                ml_score=score,
                anomaly_flag=False,
                transaction_time=datetime.utcnow() - timedelta(minutes=random.randint(1, 1440))
            )
            normal_txs.append(tx)
            session.add(tx)
            
        # 15 Suspicious Transactions
        suspicious_txs = []
        for i in range(15):
            # Mix normal senders and mule receivers
            sender = random.choice(accounts) if random.random() > 0.5 else random.choice(mule_accounts)
            receiver = random.choice(mule_accounts)
            
            tx_id = str(uuid.uuid4())
            amount = round(random.uniform(500000.0, 2000000.0), 2)  # High amounts
            score = random.uniform(0.75, 0.99)
            
            tx = Transaction(
                id=tx_id,
                sender_account_id=sender.id,
                receiver_account_id=receiver.id,
                amount=amount,
                transaction_type=random.choice(["RTGS", "IMPS"]),
                geo_location=random.choice(LOCATIONS),
                ml_score=score,
                anomaly_flag=True,
                transaction_time=datetime.utcnow() - timedelta(minutes=random.randint(1, 60))
            )
            suspicious_txs.append(tx)
            session.add(tx)
            
        await session.flush()
        
        # Create Alerts for the suspicious transactions
        for tx in suspicious_txs:
            alert = Alert(
                id=str(uuid.uuid4()),
                transaction_id=tx.id,
                account_id=tx.sender_account_id,
                severity="HIGH",
                alert_type="GENERAL_FRAUD",
                confidence=tx.ml_score,
                status="OPEN"
            )
            session.add(alert)
            
        await session.commit()
        print(f"Inserted 200 normal transactions.")
        print(f"Inserted 15 suspicious transactions with alerts.")
        print("Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
