import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "rakshak-backend"}

async def test_predict_endpoint(async_client: AsyncClient):
    # This requires DB models and tables to be setup
    tx_payload = {
        "sender_account_id": "ACCT-001",
        "receiver_account_id": "ACCT-002",
        "amount": 500.0,
        "transaction_type": "ONLINE",
        "ip_address": "127.0.0.1",
        "device_id": "DEV-01"
    }
    response = await async_client.post("/api/v1/predict/", json=tx_payload)
    assert response.status_code == 200
    data = response.json()
    assert "final_risk_score" in data
    assert "fraud_probability" in data
