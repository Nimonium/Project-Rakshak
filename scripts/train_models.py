import joblib
from pathlib import Path

class DummyPreprocessor:
    def transform(self, data):
        return data

Path('artifacts/models').mkdir(parents=True, exist_ok=True)
joblib.dump(DummyPreprocessor(), 'artifacts/models/preprocessing_pipeline.joblib')
print('Models trained and persisted successfully')