# Project Rakshak 🛡️

Project Rakshak is an Enterprise Fraud Intelligence platform designed to monitor, detect, and analyze suspicious financial transactions and mule networks in real-time.

## Features
- **Real-time Transaction Monitoring**: Live WebSocket stream analyzing transactions and calculating risk scores.
- **Mule Graph Intelligence**: Visualize and trace complex money laundering networks and clustered mule accounts.
- **Risk Engine Intelligence**: Configurable anomaly detection using Isolation Forests and XGBoost models.
- **Regulatory Feeds**: Synchronize and apply blocklists from external authorities like RBI, CERT-In, and NCRP automatically.
- **Interactive Dashboards**: High-level overview of global fraud geography, system risk scores, and recent transaction anomalies.

## Technology Stack
- **Backend**: Python, FastAPI, SQLAlchemy, WebSockets
- **Frontend**: HTML5, Vanilla JavaScript, CSS3
- **Machine Learning**: Scikit-Learn, XGBoost

## Getting Started

### Prerequisites
- Python 3.9+

### Running the Backend
1. Navigate to the `backend` directory.
2. Install the required Python dependencies.
3. Start the FastAPI application:
   ```bash
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
4. The API will be available at `http://127.0.0.1:8000` (Swagger UI at `/docs`).

### Running the Frontend
1. Navigate to the `frontend/rakshak` directory.
2. Serve the static files using Python's built-in HTTP server:
   ```bash
   python -m http.server 3000
   ```
3. Open your browser and navigate to `http://127.0.0.1:3000`.

## Architecture
- `backend/app/main.py`: Entry point for the FastAPI application.
- `backend/app/api/`: REST and WebSocket API routes.
- `backend/app/schemas/`: Pydantic models for data validation.
- `backend/app/db/`: Database configuration and ORM models.
- `frontend/rakshak/`: Static assets for the user interface.
