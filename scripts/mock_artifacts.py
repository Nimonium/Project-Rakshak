import joblib
from pathlib import Path

class DummyXGB:
    def predict_proba(self, X): 
        return [[0.1, 0.9]] * len(X)

class DummyISO:
    def predict(self, X): 
        return [1] * len(X)

Path('artifacts/models').mkdir(parents=True, exist_ok=True)
joblib.dump(DummyXGB(), 'artifacts/models/xgboost_model.joblib')
joblib.dump(DummyISO(), 'artifacts/models/isolation_forest.joblib')
print('All ML artifacts generated successfully')
