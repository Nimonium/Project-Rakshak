import json
import logging
from typing import Tuple, List, Dict
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.impute import SimpleImputer
import structlog
import os

logger = structlog.get_logger(__name__)

class FeatureEngineeringPipeline:
    def __init__(self):
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = RobustScaler() # Robust to outliers
        
        # High signal features provided in specs
        self.high_signal_features = [
            "F115", "F321", "F527", "F531", "F670", "F1692", "F2082", 
            "F2122", "F2582", "F2678", "F2737", "F2956", "F3043", "F3836", 
            "F3887", "F3889", "F3891", "F3894"
        ]
        self.target_col = "F3924"
        
        self.feature_columns: List[str] = []

    def load_data(self, file_path: str) -> pd.DataFrame:
        """Loads JSON dataset into a pandas DataFrame."""
        logger.info(f"Loading dataset from {file_path}")
        with open(file_path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        logger.info(f"Dataset loaded with shape {df.shape}")
        return df

    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced time-based features."""
        if 'transaction_time' in df.columns:
            df['transaction_time'] = pd.to_datetime(df['transaction_time'])
            df['hour_of_day'] = df['transaction_time'].dt.hour
            df['day_of_week'] = df['transaction_time'].dt.dayofweek
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            
            # Simple temporal anomaly: transactions between 12 AM and 4 AM
            df['is_night_transaction'] = df['hour_of_day'].isin([0, 1, 2, 3, 4]).astype(int)
            
            # Sort for rolling window calculations
            df.sort_values(by=['sender_account_id', 'transaction_time'], inplace=True)
            
            # Burst Windows (Transactions within 5 mins)
            # This requires a proper DateTime index in pandas or a groupby diff
            df['time_diff'] = df.groupby('sender_account_id')['transaction_time'].diff().dt.total_seconds()
            df['is_burst'] = (df['time_diff'] < 300).astype(int) # Under 5 mins
            
        return df

    def create_behavioral_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create velocity, frequency, behavioral, and entropy features."""
        if 'sender_account_id' in df.columns:
            # Transaction frequency
            freq = df.groupby('sender_account_id').size().reset_index(name='sender_freq')
            df = df.merge(freq, on='sender_account_id', how='left')
            
            if 'amount' in df.columns:
                # Average outgoing amount
                avg_amt = df.groupby('sender_account_id')['amount'].mean().reset_index(name='avg_outgoing_amount')
                df = df.merge(avg_amt, on='sender_account_id', how='left')
                
                # Sudden spike ratio
                df['amount_spike_ratio'] = df['amount'] / (df['avg_outgoing_amount'] + 1e-5)
            
            # Beneficiary uniqueness (Fan-out)
            if 'receiver_account_id' in df.columns:
                fan_out = df.groupby('sender_account_id')['receiver_account_id'].nunique().reset_index(name='fan_out')
                df = df.merge(fan_out, on='sender_account_id', how='left')
                
                # Transaction entropy heuristic (number of unique receivers / total txs)
                df['tx_entropy'] = df['fan_out'] / (df['sender_freq'] + 1e-5)
                
                # Fan-in: Number of unique senders per receiver
                fan_in = df.groupby('receiver_account_id')['sender_account_id'].nunique().reset_index(name='fan_in')
                df = df.merge(fan_in, on='receiver_account_id', how='left')
                

        # Fill only numeric columns
       # Fill numeric NaNs
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)

        # Fill categorical/string NaNs
        object_cols = df.select_dtypes(include=["object", "string", "category"]).columns
        for col in object_cols:
         df[col] = df[col].fillna("unknown")

        return df

    def handle_missing_and_scale(self, df: pd.DataFrame, is_train: bool = True):
        """Imputes missing values and scales features robustly."""

        y = None

        # Separate target column
        if self.target_col in df.columns:
           y = df[self.target_col]
           X = df.drop(columns=[self.target_col])
        else:
            X = df.copy()

         # Columns that should never be used as ML features
        exclude_cols = [
            "id",
            "transaction_id",
            "sender_account_id",
            "receiver_account_id",
            "transaction_time"
        ]

        # Get numeric columns
        num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        num_cols = [c for c in num_cols if c not in exclude_cols]

        # Ensure BOI high-signal features are included
        for col in self.high_signal_features:
            if col in X.columns and col not in num_cols:
               num_cols.append(col)

        # Create feature dataframe
        X_num = X[num_cols].copy()

        # Convert everything possible to numeric
        for col in X_num.columns:
           X_num[col] = pd.to_numeric(X_num[col], errors="coerce")

        # Replace infinite values
        X_num = X_num.replace([np.inf, -np.inf], np.nan)

        print(f"Feature matrix shape: {X_num.shape}")

        if is_train:

           self.feature_columns = X_num.columns.tolist()

           valid_cols = X_num.columns[X_num.notna().any()].tolist()
           self.feature_columns = valid_cols
           X_num = X_num[self.feature_columns]

           print("STARTING IMPUTER")
           X_imputed = self.imputer.fit_transform(X_num)
           print("Shape after imputation:", X_imputed.shape)
           print("IMPUTER DONE")

           print("STARTING SCALER")
           X_scaled = self.scaler.fit_transform(X_imputed)
           print("SCALER DONE")

        else:

            # Add missing columns from training
            missing_cols = set(self.feature_columns) - set(X_num.columns)

            for col in missing_cols:
                X_num[col] = 0

            X_num = X_num[self.feature_columns]

            print("STARTING TEST IMPUTER")
            X_imputed = self.imputer.transform(X_num)
            print("TEST IMPUTER DONE")

            print("STARTING TEST SCALER")
            X_scaled = self.scaler.transform(X_imputed)
            print("TEST SCALER DONE")

        X_final = pd.DataFrame(
            X_scaled,
            columns=self.feature_columns,
            index=X.index
        )

        return X_final, y

    def process_pipeline(self, file_path: str = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Runs the complete pipeline and splits data."""

        if file_path:
            df = self.load_data(file_path)
        else:
            from backend.app.ml.feature_engineering.dataset_loader import DatasetLoader
            loader = DatasetLoader()
            df = loader.load_and_merge()

        if df.empty:
             raise ValueError("No data to process!")

        print("STEP 1: Dataset loaded")

        df = self.create_temporal_features(df)
        print("STEP 2: Temporal features created")

        df = self.create_behavioral_features(df)
        print("STEP 3: Behavioral features created")

        print("STEP 4: Starting train-test split")

        train_df, test_df = train_test_split(
            df,
            test_size=0.2,
            random_state=42,
            stratify=df[self.target_col] if self.target_col in df.columns else None
        )

        print("STEP 5: Train-test split completed")

        X_train, y_train = self.handle_missing_and_scale(train_df, is_train=True)
        print("STEP 6: X_train created")

        X_test, y_test = self.handle_missing_and_scale(test_df, is_train=False)
        print("STEP 7: X_test created")

        os.makedirs("artifacts/data", exist_ok=True)
        print("STEP 8: Saving parquet files")

        X_train.to_parquet("artifacts/data/X_train.parquet")
        X_test.to_parquet("artifacts/data/X_test.parquet")

        if y_train is not None:
            pd.DataFrame(y_train).to_parquet("artifacts/data/y_train.parquet")
            pd.DataFrame(y_test).to_parquet("artifacts/data/y_test.parquet")

        print("STEP 9: Parquet files saved")

        logger.info(
           f"Pipeline complete. Train shape: {X_train.shape}, Test shape: {X_test.shape}"
        )

        return X_train, X_test, y_train, y_test