import joblib
import numpy as np
from pathlib import Path
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

# The scoring service creates 51 features (F0-F49 + amount)
# Mock models must be trained with matching feature count
N_FEATURES = 51
N_SAMPLES = 20

np.random.seed(42)
X_dummy = np.random.randn(N_SAMPLES, N_FEATURES)
y_dummy = np.random.randint(0, 2, N_SAMPLES)

xgb_model = DummyClassifier(strategy="constant", constant=1)
xgb_model.fit(X_dummy, y_dummy)

iso_model = IsolationForest(n_estimators=10, random_state=42)
iso_model.fit(X_dummy)

preprocessing_pipeline = Pipeline([
    ('passthrough', FunctionTransformer(func=None))
])
preprocessing_pipeline.fit(X_dummy)

Path('artifacts/models').mkdir(parents=True, exist_ok=True)
joblib.dump(xgb_model, 'artifacts/models/xgboost_model.joblib')
joblib.dump(iso_model, 'artifacts/models/isolation_forest.joblib')
joblib.dump(preprocessing_pipeline, 'artifacts/models/preprocessing_pipeline.joblib')
print('All ML artifacts generated successfully (51 features)')
