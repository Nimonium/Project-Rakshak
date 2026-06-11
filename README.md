# 🛡️ Rakshak – AI-Powered Mule Account & Fraud Intelligence Platform

## Overview

Rakshak is an AI-driven fraud detection and mule account intelligence platform developed for the **Bank of India Hackathon 2026**. The system leverages machine learning, anomaly detection, graph analytics, and explainable AI to proactively identify suspicious transactions and mule account networks before fraudulent proceeds can circulate through the banking ecosystem.

The platform provides investigators and financial institutions with real-time risk scoring, network visualization, regulatory feed integration, and intelligent alert generation.

---

## Problem Statement

Banks are increasingly facing cyber-enabled financial fraud involving mule accounts used to receive, transfer, and conceal illicit funds across multiple banking channels.

Traditional rule-based systems struggle to detect evolving fraud patterns in real time.

Rakshak addresses this challenge by combining:

* Behavioral Machine Learning
* Graph-Based Mule Detection
* Real-Time Transaction Monitoring
* Explainable AI
* Regulatory Feed Correlation
* Cross-Channel Fraud Intelligence

---

# Key Features

### AI-Powered Fraud Detection

* Supervised mule account classification
* Suspicious transaction prediction
* Dynamic fraud risk scoring

### Anomaly Detection

* Detection of previously unseen fraud patterns
* Behavioral deviation monitoring
* Adaptive intelligence

### Graph Intelligence

* Mule network discovery
* Circular fund movement detection
* Fan-in/Fan-out identification
* Shared device and IP correlation

### Explainable AI

* SHAP-based explanations
* Feature contribution analysis
* Investigator-friendly reasoning

### Real-Time Monitoring

* Live alert dashboard
* Streaming transaction simulation
* Instant risk updates

### Regulatory Intelligence

* NCRP alert integration
* CERT-In watchlist simulation
* RBI/FIU regulatory feed support

### Investigator Workflow

* Alert triaging
* Case escalation
* Account freezing recommendations
* STR/SAR generation support

---

# System Architecture

```
Frontend (React Dashboard)
        ↓
FastAPI Backend
        ↓
Feature Engineering Pipeline
        ↓
ML Inference Engine
        ↓
Graph Intelligence Layer
        ↓
Unified Risk Scoring Engine
        ↓
Alert & Decision System
```

---

# Project Structure

```
Rakshak/
│
├── frontend/
│   └── rakshak/
│       ├── app.js
│       ├── index.html
│       ├── organization.html
│       ├── profile.html
│       └── styles.css
│
├── backend/
│   │
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   ├── deps.py
│   │   │   └── router.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── logging.py
│   │   │   └── websocket_manager.py
│   │   │
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── models/
│   │   │
│   │   ├── ml/
│   │   │   ├── training/
│   │   │   ├── inference/
│   │   │   ├── explainability/
│   │   │   ├── graph/
│   │   │   ├── anomaly/
│   │   │   └── feature_engineering/
│   │   │
│   │   ├── services/
│   │   │   ├── transaction_service.py
│   │   │   ├── alert_service.py
│   │   │   ├── graph_service.py
│   │   │   └── scoring_service.py
│   │   │
│   │   ├── schemas/
│   │   ├── workers/
│   │   ├── websocket/
│   │   └── main.py
│   │
│   ├── scripts/
│   ├── tests/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── README.md
│
└── README.md
```

---

# Technology Stack

## Frontend

* HTML5
* CSS3
* JavaScript
* Charting Libraries
* Graph Visualization Libraries

## Backend

* FastAPI
* Python
* WebSockets
* REST APIs

## Machine Learning

* XGBoost
* LightGBM
* Isolation Forest
* SHAP

## Data & Storage

* PostgreSQL
* Redis (Optional)

## Visualization

* Cytoscape.js
* D3.js

## Deployment

* Docker
* Docker Compose

---

# AI/ML Pipeline

## 1. Feature Engineering

* Missing value handling
* Data normalization
* Feature selection
* Behavioral feature extraction

Target Variable:

```
Feature3924
```

Important Features:

```
F115
F321
F527
F531
F670
F1692
F2082
F2122
F2582
F2678
F2737
F2956
F3043
F3836
F3887
F3889
F3891
F3894
```

---

## 2. Supervised Learning

Algorithms:

* XGBoost
* LightGBM
* Random Forest

Use Cases:

* Mule Account Classification
* Fraud Probability Estimation

---

## 3. Unsupervised Learning

Algorithms:

* Isolation Forest
* One-Class SVM
* DBSCAN

Use Cases:

* Novel Fraud Detection
* Emerging Fraud Pattern Discovery

---

## 4. Graph Analytics

Nodes:

* Accounts
* Devices
* Mobile Numbers
* IP Addresses
* Beneficiaries

Edges:

* Fund Transfers
* Shared Devices
* Shared IPs
* Shared KYC Elements

Capabilities:

* Ring Detection
* Community Detection
* Layering Identification
* Mule Chain Discovery

---

# Risk Scoring Framework

```
Final Risk Score =
0.40 × ML Score +
0.30 × Anomaly Score +
0.20 × Graph Risk +
0.10 × Regulatory Rule Score
```

Risk Categories:

* 0–30 : Low Risk
* 31–60 : Medium Risk
* 61–100 : High Risk

---

# Running the Project

## Backend

Navigate to backend:

```bash
cd backend
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run FastAPI:

```bash
uvicorn app.main:app --reload
```

Backend URL:

```
http://localhost:8000
```

API Documentation:

```
http://localhost:8000/docs
```

---

## Frontend

Navigate to frontend:

```bash
cd frontend/rakshak
```

Open:

```bash
index.html
```

Or serve locally using:

```bash
python -m http.server 5500
```

Frontend URL:

```
http://localhost:5500
```

---

# Team Responsibilities

### Member A

Frontend Dashboard Development

### Member B

UI/UX, Investigator Portal, Explainability Screens

### Member C

Backend APIs, Services, WebSockets

### Member D

Machine Learning, Feature Engineering, Graph Analytics

---

# Future Enhancements

* Federated Learning Across Banks
* Real Government Feed Integration
* Generative AI Investigator Copilot
* Adaptive Continuous Retraining
* Multi-Bank Threat Intelligence Network

---

# Impact

Rakshak transforms fraud detection from reactive monitoring to proactive prevention by enabling financial institutions to identify mule networks, explain AI decisions, and contain fraudulent proceeds before they propagate through the ecosystem.

**"Detect Early. Explain Clearly. Prevent Proactively."**
