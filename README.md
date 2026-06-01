## Project Structure

### Backend and Frontend
```text

backend/
│
├── app/
│   ├── api/
│   │   ├── routes/
│   │   ├── deps.py
│   │   └── router.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── logging.py
│   │   └── websocket_manager.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── models/
│   │
│   ├── ml/
│   │   ├── training/
│   │   ├── inference/
│   │   ├── explainability/
│   │   ├── graph/
│   │   ├── anomaly/
│   │   └── feature_engineering/
│   │
│   ├── services/
│   │   ├── transaction_service.py
│   │   ├── alert_service.py
│   │   ├── graph_service.py
│   │   └── scoring_service.py
│   │
│   ├── schemas/
│   ├── workers/
│   ├── websocket/
│   └── main.py
│
├── scripts/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md



frontend/
│
├── src/
│
├── app/
│   ├── routes/
│   ├── providers/
│   └── layouts/
│
├── components/
│   ├── dashboard/
│   ├── graph/
│   ├── alerts/
│   ├── transactions/
│   ├── explainability/
│   ├── investigator/
│   ├── feeds/
│   └── shared/
│
├── pages/
│   ├── Landing.tsx
│   ├── Login.tsx
│   ├── Dashboard.tsx
│   ├── Transactions.tsx
│   ├── GraphView.tsx
│   ├── Alerts.tsx
│   ├── RiskEngine.tsx
│   ├── Explainability.tsx
│   ├── InvestigatorCase.tsx
│   └── Settings.tsx
│
├── services/
│   ├── api.ts
│   ├── auth.service.ts
│   ├── transaction.service.ts
│   ├── alert.service.ts
│   ├── graph.service.ts
│   └── websocket.service.ts
│
├── store/
│   ├── auth.store.ts
│   ├── dashboard.store.ts
│   ├── graph.store.ts
│   └── alert.store.ts
│
├── hooks/
│   ├── useAuth.ts
│   ├── useWebSocket.ts
│   └── useRiskScores.ts
│
├── types/
├── utils/
├── styles/
├── public/
├── package.json
├── vite.config.ts
└── tsconfig.json
