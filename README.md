# 🛡️ Project-Rakshak

> Enterprise-grade Banking Fraud Intelligence Platform for detecting suspicious accounts, mule account networks, money laundering patterns, and fraudulent fund movements in real-time.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Async-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Redis](https://img.shields.io/badge/Redis-Cache-red)
![XGBoost](https://img.shields.io/badge/XGBoost-ML-orange)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

# 📌 Overview

Project-Rakshak is an AI-powered fraud intelligence platform built for modern banking ecosystems. The system combines Machine Learning, Graph Analytics, Real-Time Streaming, and Explainable AI to identify:

* 🚨 Mule Accounts
* 🚨 Money Laundering Chains
* 🚨 Fraud Rings
* 🚨 Suspicious Fund Movements
* 🚨 High-Risk Banking Accounts

The platform provides real-time risk scoring, anomaly detection, graph-based investigations, and explainable fraud decisions for analysts and investigators.

---

# ✨ Key Features

## 🔍 Fraud Detection Engine

* Real-time transaction scoring
* ML-based anomaly detection
* Behavioral risk profiling
* Fraud likelihood prediction
* Dynamic risk score calculation

---

## 🕸️ Graph Intelligence

* Account relationship mapping
* Mule account detection
* Circular transaction detection
* Community detection using Louvain clustering
* Suspicious path discovery

Example:

ACC_0023 → ACC_0090 → MULE_0001

The system automatically identifies suspicious fund routes and money movement chains.

---

## 🤖 Machine Learning Pipeline

### Models Used

* XGBoost Classifier
* Isolation Forest
* Ensemble Risk Scoring

### Features

* Automated feature engineering
* Hyperparameter tuning with Optuna
* Multi-shard dataset ingestion
* Model evaluation reports
* Production-ready inference pipeline

---

## 📊 Explainable AI (XAI)

Project-Rakshak provides complete transparency for fraud decisions using SHAP.

### Outputs

* SHAP Waterfall Plots
* Feature Importance Analysis
* Prediction Explanations
* Fraud Driver Identification

---

## ⚡ Real-Time Streaming

* WebSocket transaction feed
* Live fraud alerts
* Streaming risk updates
* Continuous monitoring

WebSocket Endpoint:

ws://localhost:8000/ws/transactions

---

## 📈 Observability & Metrics

Prometheus metrics are exposed for monitoring:

* Fraud detection rate
* Inference latency
* Active websocket connections
* Throughput statistics

Endpoint:

http://localhost:8000/api/v1/metrics

---

# 🏗️ System Architecture

Backend Stack:

* FastAPI (Async)
* PostgreSQL
* Redis
* SQLAlchemy
* AsyncPG

AI & Analytics:

* XGBoost
* Isolation Forest
* SHAP
* NetworkX
* Optuna

Infrastructure:

* Docker
* Docker Compose
* WebSockets

---

# 📂 Project Structure

```text
Project-Rakshak/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── ml/
│   │   ├── graph/
│   │   └── services/
│   │
│   └── data/
│
├── scripts/
│
├── tests/
│
├── artifacts/
│   ├── models/
│   ├── evaluation/
│   ├── reports/
│   ├── graph/
│   └── shap/
│
├── docker-compose.yml
└── README.md
```

---

# 🚀 Quick Start

## Prerequisites

* Docker
* Docker Compose
* Python 3.11+
* UV Package Manager (Optional)

---

# 🐳 Docker Deployment

Start the complete stack:

```bash
docker-compose up -d --build
```

API:

```text
http://localhost:8000
```

Swagger Documentation:

```text
http://localhost:8000/docs
```

---

# 💻 Local Development

Install dependencies:

```bash
uv pip install -e .
```

Start PostgreSQL and Redis:

```bash
docker-compose up -d postgres redis
```

Run migrations:

```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

Start server:

```bash
uvicorn backend.app.main:app --reload
```

---

# 🧠 Advanced ML Pipeline

## Step 1 — Dataset Preparation

Place dataset shards inside:

```text
backend/data/
```

Example:

```text
DataSet_part1.json
DataSet_part2.json
DataSet_part3.json
```

---

## Step 2 — Feature Engineering

```bash
python backend/app/ml/feature_engineering/pipeline.py
```

Generated outputs:

```text
artifacts/reports/
```

---

## Step 3 — Model Training

```bash
python backend/app/ml/training/train.py
```

Generated outputs:

```text
artifacts/models/
artifacts/evaluation/
```

---

# 🔥 Dataset Replay Engine

Simulate real banking traffic.

## Normal Traffic

```bash
python scripts/replay_dataset.py --mode normal --speed 1.0
```

## Fraud Heavy Scenario

```bash
python scripts/replay_dataset.py --mode fraud-heavy --speed 2.0
```

## Stress Testing

```bash
python scripts/replay_dataset.py --mode stress-test --speed 5.0
```

---

# 🔍 Example Fraud Investigation

### Detected Mule Account

```json
{
  "id": "MULE_0001",
  "risk_score": 0.8767,
  "anomaly_score": 0.7433,
  "graph_score": 0.95,
  "is_frozen": true
}
```

### Suspicious Path

```text
ACC_0023
      ↓
ACC_0090
      ↓
MULE_0001
```

### High Value Transfers

```text
₹19,88,303.74
₹18,97,464.55
```

The system automatically flags the account, freezes activity, and generates investigation graphs.

---

# 📊 Benchmarking

Run performance tests:

```bash
python tests/benchmarks/test_throughput.py
```

Generated Reports:

```text
artifacts/reports/
```

---

# 📈 SHAP Visualizations

Generated automatically:

```text
artifacts/shap/
```

Examples:

```text
waterfall_plot.png
feature_importance.png
```

---

# 🕸️ Graph Analytics Exports

Generated outputs:

```text
artifacts/graph/
```

Includes:

* Louvain Communities
* Mule Networks
* Circular Money Flows
* Fraud Ring Structures

---

# 🔐 Security Features

* Risk-based account freezing
* Fraud ring detection
* Real-time anomaly alerts
* Explainable AI decisions
* Transaction network analysis
* Continuous fraud monitoring

---

# 🎯 Future Enhancements

* Neo4j Graph Database Integration
* Kafka Event Streaming
* Real-Time Investigator Dashboard
* Federated Learning Support
* Multi-Bank Fraud Intelligence Sharing
* LLM-Powered Fraud Investigation Assistant

---

# 👨‍💻 Author

Developed as an enterprise-scale fraud intelligence and anti-money laundering platform leveraging Machine Learning, Graph Analytics, and Explainable AI.

---

## ⭐ Support

If you found this project useful:

⭐ Star the repository

🍴 Fork the repository

🛡️ Help build safer financial systems
