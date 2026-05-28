from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge

router = APIRouter()

# Define Prometheus Metrics
INFERENCE_REQUESTS = Counter(
    "rakshak_inference_requests_total",
    "Total number of inference requests"
)

FRAUD_DETECTED = Counter(
    "rakshak_fraud_detected_total",
    "Total number of fraudulent transactions detected",
    ["severity"]
)

INFERENCE_LATENCY = Histogram(
    "rakshak_inference_latency_seconds",
    "Latency of inference endpoint",
    buckets=[0.05, 0.1, 0.15, 0.2, 0.5, 1.0]
)

ACTIVE_WEBSOCKETS = Gauge(
    "rakshak_active_websockets",
    "Number of currently connected WebSocket clients"
)

@router.get("/", response_class=PlainTextResponse)
async def get_metrics():
    """
    Exposes Prometheus metrics.
    """
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
