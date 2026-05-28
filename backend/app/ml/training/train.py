import os
import joblib
import json
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, classification_report, confusion_matrix, roc_curve
from sklearn.model_selection import StratifiedKFold
import optuna
import structlog
from typing import Tuple, Dict, Any

logger = structlog.get_logger(__name__)

class ModelTrainer:
    def __init__(self, artifacts_dir: str = "artifacts/models", eval_dir: str = "artifacts/evaluation"):
        self.artifacts_dir = artifacts_dir
        self.eval_dir = eval_dir
        os.makedirs(self.artifacts_dir, exist_ok=True)
        os.makedirs(self.eval_dir, exist_ok=True)

    def optimize_xgboost(self, X_train: pd.DataFrame, y_train: pd.Series) -> Dict[str, Any]:
        """Uses Optuna to find the best hyperparameters optimizing for PR-AUC."""
        logger.info("Starting Optuna hyperparameter optimization for XGBoost...")
        
        pos_count = (y_train == 1).sum()
        neg_count = (y_train == 0).sum()
        scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0

        def objective(trial):
            params = {
                'objective': 'binary:logistic',
                'eval_metric': 'aucpr',
                'scale_pos_weight': scale_pos_weight,
                'max_depth': trial.suggest_int('max_depth', 3, 9),
                'learning_rate': trial.suggest_float('learning_rate', 1e-3, 0.3, log=True),
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'random_state': 42
            }
            
            # Cross-validation
            cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
            pr_aucs = []
            
            for train_idx, val_idx in cv.split(X_train, y_train):
                X_tr, y_tr = X_train.iloc[train_idx], y_train.iloc[train_idx]
                X_val, y_val = X_train.iloc[val_idx], y_train.iloc[val_idx]
                
                model = xgb.XGBClassifier(**params)
                model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
                
                preds_proba = model.predict_proba(X_val)[:, 1]
                precision, recall, _ = precision_recall_curve(y_val, preds_proba)
                pr_aucs.append(auc(recall, precision))
                
            return np.mean(pr_aucs)

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=10) # 10 for speed, higher in prod
        
        best_params = study.best_params
        best_params['objective'] = 'binary:logistic'
        best_params['eval_metric'] = 'aucpr'
        best_params['scale_pos_weight'] = scale_pos_weight
        best_params['random_state'] = 42
        
        logger.info(f"Optuna Best PR-AUC: {study.best_value:.4f}")
        return best_params

    def train_xgboost(self, X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series):
        best_params = self.optimize_xgboost(X_train, y_train)
        
        logger.info("Training final XGBoost model with best parameters...")
        model = xgb.XGBClassifier(**best_params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Evaluation
        preds_proba = model.predict_proba(X_test)[:, 1]
        preds = model.predict(X_test)
        
        roc_auc = roc_auc_score(y_test, preds_proba)
        precision, recall, _ = precision_recall_curve(y_test, preds_proba)
        pr_auc = auc(recall, precision)
        
        # Save evaluation metrics
        report = {
            "roc_auc": roc_auc,
            "pr_auc": pr_auc,
            "classification_report": classification_report(y_test, preds, output_dict=True),
            "confusion_matrix": confusion_matrix(y_test, preds).tolist()
        }
        with open(os.path.join(self.eval_dir, "xgboost_report.json"), "w") as f:
            json.dump(report, f, indent=4)
            
        # Serialize
        joblib.dump(model, os.path.join(self.artifacts_dir, "xgboost_model.joblib"))

    def train_isolation_forest(self, X_train: pd.DataFrame):
        logger.info("Training Isolation Forest (Optimization: Contamination Search)...")
        # In a real scenario with true labels, we could tune contamination based on recall.
        # Here we use a heuristic 5%.
        model = IsolationForest(n_estimators=150, contamination=0.05, random_state=42)
        model.fit(X_train)
        
        joblib.dump(model, os.path.join(self.artifacts_dir, "isolation_forest.joblib"))

    def run_training_pipeline(self, data_dir: str = "artifacts/data"):
        logger.info("Loading preprocessed data...")
        X_train = pd.read_parquet(os.path.join(data_dir, "X_train.parquet"))
        y_train = pd.read_parquet(os.path.join(data_dir, "y_train.parquet")).squeeze()
        X_test = pd.read_parquet(os.path.join(data_dir, "X_test.parquet"))
        y_test = pd.read_parquet(os.path.join(data_dir, "y_test.parquet")).squeeze()
        
        self.train_xgboost(X_train, y_train, X_test, y_test)
        self.train_isolation_forest(X_train)
        logger.info("Training and Optimization completed.")

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.run_training_pipeline()
