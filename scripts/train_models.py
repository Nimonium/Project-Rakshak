# backend/app/ml/training/train.py
# FIXED VERSION — run this ONCE to generate joblib artifacts

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_selection import VarianceThreshold
import xgboost as xgb
import shap
import joblib, json, os

DATA_PATH = "DataSet_1_.json"          # or .csv — change extension accordingly
ARTIFACTS = "artifacts/models/"
os.makedirs(ARTIFACTS, exist_ok=True)

# ── 1. Load ──────────────────────────────────────────────────────────────────
# Using a dummy DataFrame for the mock pipeline to work without actual dataset
# In production, read from DATA_PATH
df = pd.DataFrame(np.random.rand(100, 3924), columns=[f"F{i}" for i in range(3924)])
df["F3924"] = np.random.randint(0, 2, 100) # Target variable

y = df["F3924"].values
X = df.drop("F3924", axis=1)

# ── 2. Preprocessing ─────────────────────────────────────────────────────────
null_pct = X.isna().sum() / len(X)
X = X.loc[:, null_pct < 0.8]                       # drop >80% null cols

for c in X.select_dtypes(include="object").columns: # encode categoricals
    le = LabelEncoder()
    X[c] = le.fit_transform(X[c].astype(str)).astype(float)

X = X.fillna(X.median())                            # fill remaining nulls

vt = VarianceThreshold(threshold=0.001)             # remove near-zero variance
X_arr = vt.fit_transform(X)
X = pd.DataFrame(X_arr, columns=X.columns[vt.get_support()])

# ── 3. Feature selection (gain-based, top 150) ────────────────────────────────
# Avoid division by zero if no 1s exist in the mock data
num_ones = (y == 1).sum()
scale_pos = (y == 0).sum() / num_ones if num_ones > 0 else 111.1 # 111.1 — critical for imbalance

selector = xgb.XGBClassifier(
    n_estimators=100, max_depth=4,
    scale_pos_weight=scale_pos, random_state=42, n_jobs=-1, tree_method="hist"
)
selector.fit(X, y)

gain_imp = pd.Series(selector.get_booster().get_score(importance_type="gain"))
gain_imp = gain_imp.reindex(X.columns).fillna(0)
# Mock data might not have 150 features with gain > 0
TOP_FEATURES = gain_imp.nlargest(150).index.tolist()
if not TOP_FEATURES:
    TOP_FEATURES = X.columns[:150].tolist()
X_sel = X[TOP_FEATURES]

joblib.dump(TOP_FEATURES, f"{ARTIFACTS}feature_names.joblib")
joblib.dump(vt, f"{ARTIFACTS}variance_threshold.joblib")

# ── 4. Train final model ──────────────────────────────────────────────────────
model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.7,
    min_child_weight=5,
    gamma=0.5,
    reg_alpha=0.5,
    reg_lambda=2.0,
    scale_pos_weight=scale_pos,
    eval_metric="aucpr",
    random_state=42,
    n_jobs=-1,
    tree_method="hist",
)
model.fit(X_sel.values, y)
joblib.dump(model, f"{ARTIFACTS}xgboost_model.joblib")
print("Model saved.")

# ── 5. Build SHAP explainer ──────────────────────────────────────────────────
explainer = shap.TreeExplainer(model)
joblib.dump(explainer, f"{ARTIFACTS}shap_explainer.joblib")
print("SHAP explainer saved.")

# ── 6. Train Isolation Forest ────────────────────────────────────────────────
from sklearn.ensemble import IsolationForest
iso = IsolationForest(random_state=42)
iso.fit(X_sel.values)
joblib.dump(iso, f"{ARTIFACTS}isolation_forest.joblib")
print("Isolation Forest saved.")