import asyncio
import httpx
import random
import time
import structlog
from typing import List, Dict, Any

logger = structlog.get_logger(__name__)

API_URL = "http://localhost:8000/api/v1/predict/"

class FraudSimulator:
    def __init__(self):
        self.accounts = [f"ACCT-{i:04d}" for i in range(1, 100)]
        self.mule_ring = ["ACCT-0090", "ACCT-0091", "ACCT-0092", "ACCT-0093", "ACCT-0094"]
        
    def _generate_normal_tx(self) -> Dict[str, Any]:
        sender = random.choice(self.accounts)
        receiver = random.choice([a for a in self.accounts if a != sender])
        return {
            "sender_account_id": sender,
            "receiver_account_id": receiver,
            "amount": random.uniform(10, 5000),
            "transaction_type": "ONLINE_TRANSFER",
            "ip_address": f"192.168.1.{random.randint(1, 255)}",
            "device_id": f"DEV-{random.randint(100, 999)}"
        }
        
    def _generate_mule_chain(self) -> List[Dict[str, Any]]:
        """Simulates A -> B -> C -> D rapid transfer."""
        amount = random.uniform(50000, 90000)
        chain = []
        for i in range(len(self.mule_ring) - 1):
            chain.append({
                "sender_account_id": self.mule_ring[i],
                "receiver_account_id": self.mule_ring[i+1],
                "amount": amount * (1.0 - (0.01 * i)), # Slight drop in amount
                "transaction_type": "WIRE_TRANSFER",
                "ip_address": "45.22.11.99",
                "device_id": "DEV-MULE-01"
            })
        return chain

    def _generate_burst(self) -> List[Dict[str, Any]]:
        """Simulates one account sending many small transactions rapidly."""
        sender = random.choice(self.accounts)
        receivers = random.sample([a for a in self.accounts if a != sender], 10)
        return [{
            "sender_account_id": sender,
            "receiver_account_id": r,
            "amount": random.uniform(9000, 9999), # Structuring below 10k
            "transaction_type": "P2P_TRANSFER",
            "ip_address": "88.99.11.22",
            "device_id": "DEV-BURST-01"
        } for r in receivers]

    async def send_transaction(self, client: httpx.AsyncClient, tx: Dict[str, Any]):
        try:
            response = await client.post(API_URL, json=tx)
            if response.status_code == 200:
                res = response.json()
                logger.info(f"Sent TX. Score: {res.get('final_risk_score', 0.0):.4f}")
            else:
                logger.error(f"Error sending TX: {response.text}")
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")

    async def run_simulation(self):
        logger.info("Starting real-time fraud simulation...")
        async with httpx.AsyncClient() as client:
            while True:
                scenario = random.random()
                
                if scenario < 0.8:
                    # 80% Normal
                    tx = self._generate_normal_tx()
                    await self.send_transaction(client, tx)
                    await asyncio.sleep(random.uniform(0.1, 0.5))
                    
                elif scenario < 0.9:
                    # 10% Burst
                    logger.warning("Simulating BURST scenario...")
                    txs = self._generate_burst()
                    for tx in txs:
                        await self.send_transaction(client, tx)
                        await asyncio.sleep(0.05)
                        
                else:
                    # 10% Mule Chain
                    logger.warning("Simulating MULE CHAIN scenario...")
                    txs = self._generate_mule_chain()
                    for tx in txs:
                        await self.send_transaction(client, tx)
                        await asyncio.sleep(0.1)

if __name__ == "__main__":
    simulator = FraudSimulator()
    asyncio.run(simulator.run_simulation())
