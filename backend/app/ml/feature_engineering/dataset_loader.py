import os
import glob
import json
import pandas as pd
import structlog
from typing import List, Tuple, Dict, Any

logger = structlog.get_logger(__name__)

class DatasetLoader:
    def __init__(self, data_dir: str = "backend/data", report_dir: str = "artifacts/reports"):
        self.data_dir = data_dir
        self.report_dir = report_dir
        os.makedirs(self.report_dir, exist_ok=True)
        self.file_pattern = os.path.join(self.data_dir, "DataSet_part*.json")
        self.files = glob.glob(self.file_pattern)

    def _optimize_memory(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimizes dataframe memory usage by downcasting and using categorical dtypes."""
        for col in df.columns:
            col_type = df[col].dtype
            
            if col_type != object:
                # Downcast numerics
                if "int" in str(col_type):
                    df[col] = pd.to_numeric(df[col], downcast="integer")
                elif "float" in str(col_type):
                    df[col] = pd.to_numeric(df[col], downcast="float")
            else:
                # Convert objects to category if unique values are low (heuristic)
                num_unique = df[col].nunique()
                num_total = len(df[col])
                if num_total > 0 and (num_unique / num_total) < 0.5:
                    df[col] = df[col].astype("category")
        return df

    def _validate_schema(self, df: pd.DataFrame, expected_cols: set) -> Tuple[pd.DataFrame, set]:
        """Ensures schema consistency and tracks columns."""
        current_cols = set(df.columns)
        if not expected_cols:
            return df, current_cols
            
        missing = expected_cols - current_cols
        if missing:
            logger.warning(f"Schema inconsistency: Missing columns {missing}. Filling with NaNs.")
            for col in missing:
                df[col] = pd.NA
                
        return df, expected_cols.union(current_cols)

    def load_and_merge(self) -> pd.DataFrame:
        """Loads all dataset shards iteratively, optimizes memory, and merges them."""
        logger.info(f"Discovered {len(self.files)} dataset shards matching {self.file_pattern}")
        
        if not self.files:
            logger.error("No dataset files found!")
            return pd.DataFrame()
            
        dfs = []
        expected_cols = set()
        total_rows = 0
        corrupt_rows = 0
        
        for file in sorted(self.files):
            logger.info(f"Processing shard: {file}")
            try:
                # Attempt to read as a normal JSON array first
                df = pd.read_json(file)
            except ValueError:
                # Fallback to JSON Lines if standard JSON parsing fails
                logger.warning(f"Failed to parse {file} as standard JSON array. Trying JSON Lines format.")
                try:
                    df = pd.read_json(file, lines=True)
                except Exception as e:
                    logger.error(f"Failed to read {file}: {str(e)}")
                    continue
            
            # Detect corruption (e.g., completely empty rows)
            initial_len = len(df)
            df.dropna(how='all', inplace=True)
            corrupt_rows += (initial_len - len(df))
            
            df, expected_cols = self._validate_schema(df, expected_cols)
            df = self._optimize_memory(df)
            
            total_rows += len(df)
            dfs.append(df)
            
        if not dfs:
            return pd.DataFrame()
            
        logger.info("Merging dataset shards...")
        final_df = pd.concat(dfs, ignore_index=True)
        
        # Generate reports
        self._generate_reports(final_df, total_rows, corrupt_rows)
        
        return final_df

    def _generate_reports(self, df: pd.DataFrame, total_rows: int, corrupt_rows: int):
        """Generates ingestion and quality reports."""
        logger.info("Generating dataset reports...")
        
        # 1. Ingestion Statistics
        stats = {
            "total_files_processed": len(self.files),
            "total_rows": total_rows,
            "corrupt_rows_removed": corrupt_rows,
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
            "columns": len(df.columns)
        }
        with open(os.path.join(self.report_dir, "ingestion_stats.json"), "w") as f:
            json.dump(stats, f, indent=4)
            
        # 2. Null Report
        null_report = df.isnull().sum().to_dict()
        with open(os.path.join(self.report_dir, "null_report.json"), "w") as f:
            json.dump(null_report, f, indent=4)
            
        # 3. Target Distribution (if F3924 exists)
        if "F3924" in df.columns:
            dist = df["F3924"].value_counts().to_dict()
            # Convert keys to str for JSON serialization
            dist = {str(k): int(v) for k, v in dist.items()}
            with open(os.path.join(self.report_dir, "target_distribution.json"), "w") as f:
                json.dump(dist, f, indent=4)
                
        logger.info(f"Reports saved to {self.report_dir}")

if __name__ == "__main__":
    loader = DatasetLoader()
    df = loader.load_and_merge()
    print(f"Final Dataframe shape: {df.shape}")
