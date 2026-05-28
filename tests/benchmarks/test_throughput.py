import asyncio
import time
import httpx
import json
import os
import structlog
from typing import List, Dict, Any

logger = structlog.get_logger(__name__)
API_URL = "http://localhost:8000/api/v1/predict"
REPORT_DIR = "artifacts/reports"

async def send_tx(client: httpx.AsyncClient, tx: Dict[str, Any]):
    try:
        start_time = time.time()
        res = await client.post(API_URL, json=tx)
        latency = (time.time() - start_time) * 1000 # ms
        return res.status_code == 200, latency
    except Exception:
        return False, 0.0

async def run_benchmark(num_requests: int = 1000, concurrency: int = 50):
    logger.info(f"Starting benchmark: {num_requests} requests with {concurrency} concurrency")
    
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    base_tx = {
        "sender_account_id": "ACCT-BENCH-1",
        "receiver_account_id": "ACCT-BENCH-2",
        "amount": 1000.0,
        "transaction_type": "ONLINE",
        "ip_address": "127.0.0.1",
        "device_id": "DEV-BENCH-1"
    }

    start_time = time.time()
    latencies = []
    successes = 0
    failures = 0
    
    semaphore = asyncio.Semaphore(concurrency)
    
    async def bound_send(client, tx):
        async with semaphore:
            return await send_tx(client, tx)

    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [bound_send(client, base_tx.copy()) for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
        
    total_time = time.time() - start_time
    
    for success, latency in results:
        if success:
            successes += 1
            latencies.append(latency)
        else:
            failures += 1
            
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
    req_per_sec = num_requests / total_time
    
    report = {
        "total_requests": num_requests,
        "concurrency": concurrency,
        "total_time_seconds": round(total_time, 2),
        "successful_requests": successes,
        "failed_requests": failures,
        "requests_per_second": round(req_per_sec, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "max_latency_ms": round(max_latency, 2),
        "p95_latency_ms": round(p95_latency, 2)
    }
    
    report_path = os.path.join(REPORT_DIR, "benchmark_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)
        
    logger.info(f"Benchmark completed. Report saved to {report_path}")
    logger.info(f"Results: {req_per_sec:.2f} req/s | Avg Latency: {avg_latency:.2f} ms")

if __name__ == "__main__":
    asyncio.run(run_benchmark(num_requests=1000, concurrency=50))
