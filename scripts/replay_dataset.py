import asyncio
import httpx
import random
import time
import structlog
import pandas as pd
import argparse
import os
from typing import List, Dict, Any

logger = structlog.get_logger(__name__)

API_URL = "http://localhost:8000/api/v1/predict"
DATA_DIR = "backend/data"

class DatasetReplayEngine:
    def __init__(self, mode: str = "normal", speed_multiplier: float = 1.0):
        self.mode = mode
        self.speed_multiplier = speed_multiplier
        self.client = httpx.AsyncClient(timeout=30.0)
        self.transactions = []
        self._load_sample_data()
        
        # Amplifiers based on mode
        self.burst_prob = 0.05 if mode == "normal" else (0.2 if mode == "fraud-heavy" else 0.5)
        self.mule_prob = 0.05 if mode == "normal" else (0.3 if mode == "fraud-heavy" else 0.4)
        
    def _load_sample_data(self):
        """Loads a subset of the dataset into memory for replay simulation."""
        logger.info("Loading dataset shard for replay...")
        try:
            # Try to load the first part for realistic accounts/values
            file_path = os.path.join(DATA_DIR, "DataSet_part1.json")
            if os.path.exists(file_path):
                try:
                    df = pd.read_json(file_path)
                except ValueError:
                    df = pd.read_json(file_path, lines=True)
                    
                # Take a sample of 10k rows to cycle through
                df = df.sample(n=min(10000, len(df)))
                
                # We need sender/receiver to exist. If dataset lacks it, we mock it.
                if 'sender_account_id' not in df.columns:
                    accounts = [f"REAL-ACCT-{i:05d}" for i in range(1000)]
                    df['sender_account_id'] = [random.choice(accounts) for _ in range(len(df))]
                    df['receiver_account_id'] = [random.choice(accounts) for _ in range(len(df))]
                if 'amount' not in df.columns:
                    # Mock amount if missing, or use a numeric column
                    numeric_cols = df.select_dtypes(include=['float', 'int']).columns
                    if len(numeric_cols) > 0:
                        df['amount'] = df[numeric_cols[0]].abs()
                    else:
                        df['amount'] = [random.uniform(10, 5000) for _ in range(len(df))]
                        
                self.transactions = df.to_dict(orient='records')
                logger.info(f"Loaded {len(self.transactions)} transactions for replay.")
            else:
                logger.warning(f"{file_path} not found. Replay will use mocked fallback data.")
                self.transactions = []
        except Exception as e:
            logger.error(f"Error loading replay data: {str(e)}")

    def _get_base_transaction(self) -> Dict[str, Any]:
        """Gets a realistic transaction from the dataset or mocks one."""
        if self.transactions:
            tx = random.choice(self.transactions)
            return {
                "sender_account_id": str(tx.get('sender_account_id', f"ACCT-{random.randint(1,100)}")),
                "receiver_account_id": str(tx.get('receiver_account_id', f"ACCT-{random.randint(1,100)}")),
                "amount": float(tx.get('amount', random.uniform(10, 5000))),
                "transaction_type": "ONLINE",
                "ip_address": f"192.168.1.{random.randint(1,255)}",
                "device_id": f"DEV-{random.randint(100,999)}"
            }
        else:
            return {
                "sender_account_id": f"ACCT-{random.randint(1,100)}",
                "receiver_account_id": f"ACCT-{random.randint(1,100)}",
                "amount": random.uniform(10, 5000),
                "transaction_type": "ONLINE",
                "ip_address": f"192.168.1.{random.randint(1,255)}",
                "device_id": f"DEV-{random.randint(100,999)}"
            }

    async def _send(self, tx: Dict[str, Any]):
        try:
            res = await self.client.post(API_URL, json=tx)
            if res.status_code == 200:
                score = res.json().get('final_risk_score', 0.0)
                logger.info(f"[REPLAY] TX Sent: {tx['sender_account_id']} -> {tx['receiver_account_id']} (${tx['amount']:.2f}) | Score: {score:.3f}")
            else:
                logger.error(f"[REPLAY] Failed: HTTP {res.status_code}")
        except Exception as e:
            logger.error(f"[REPLAY] Network error: {str(e)}")

    async def inject_fraud_burst(self):
        """Simulates rapid fan-out."""
        logger.warning(">>> INJECTING FRAUD BURST (FAN-OUT) <<<")
        sender = f"BURST-ACCT-{random.randint(1,999)}"
        tasks = []
        for _ in range(10):
            tx = self._get_base_transaction()
            tx["sender_account_id"] = sender
            tx["amount"] = random.uniform(9000, 9999) # Structuring
            tasks.append(self._send(tx))
        await asyncio.gather(*tasks)

    async def inject_mule_chain(self):
        """Simulates layered laundering (A->B->C->D)."""
        logger.warning(">>> INJECTING MULE CHAIN <<<")
        accounts = [f"MULE-ACCT-{random.randint(1,999)}" for _ in range(5)]
        amount = random.uniform(50000, 80000)
        
        for i in range(len(accounts)-1):
            tx = self._get_base_transaction()
            tx["sender_account_id"] = accounts[i]
            tx["receiver_account_id"] = accounts[i+1]
            tx["amount"] = amount * (1 - 0.02 * i) # Minus fake fee
            await self._send(tx)
            await asyncio.sleep(0.1 / self.speed_multiplier)

    async def start(self):
        logger.info(f"Starting Replay Engine [Mode: {self.mode.upper()}, Speed: {self.speed_multiplier}x]")
        
        try:
            while True:
                scenario = random.random()
                
                if scenario < self.burst_prob:
                    await self.inject_fraud_burst()
                elif scenario < (self.burst_prob + self.mule_prob):
                    await self.inject_mule_chain()
                else:
                    # Normal transaction
                    tx = self._get_base_transaction()
                    
                    if self.mode == "stress-test":
                        # Send batches asynchronously
                        tasks = [self._send(self._get_base_transaction()) for _ in range(20)]
                        await asyncio.gather(*tasks)
                    else:
                        await self._send(tx)
                        
                # Delay scaled by speed multiplier
                base_delay = 0.5 if self.mode != "stress-test" else 0.1
                await asyncio.sleep(base_delay / self.speed_multiplier)
                
        except asyncio.CancelledError:
            logger.info("Replay engine stopped.")
        finally:
            await self.client.aclose()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rakshak Dataset Replay Engine")
    parser.add_argument("--mode", type=str, choices=["normal", "fraud-heavy", "stress-test"], default="normal")
    parser.add_argument("--speed", type=float, default=1.0)
    args = parser.parse_args()
    
    engine = DatasetReplayEngine(mode=args.mode, speed_multiplier=args.speed)
    asyncio.run(engine.start())
