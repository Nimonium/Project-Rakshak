from fastapi import APIRouter
from backend.app.api.routes import predict, alerts, accounts, graph, simulate, ws, metrics, feeds, transactions, investigations

api_router = APIRouter()

api_router.include_router(predict.router, prefix="/predict", tags=["Prediction"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
api_router.include_router(graph.router, prefix="/graph", tags=["Graph Analytics"])
api_router.include_router(simulate.router, prefix="/simulate", tags=["Simulator"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Observability"])
api_router.include_router(feeds.router, prefix="/feeds", tags=["Feeds"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(investigations.router, prefix="/investigations", tags=["Investigations"])

# Root router for websockets
ws_router = APIRouter()
ws_router.include_router(ws.router, prefix="/ws", tags=["WebSockets"])
