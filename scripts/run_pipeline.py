from backend.app.ml.feature_engineering.pipeline import FeatureEngineeringPipeline

pipeline = FeatureEngineeringPipeline()

X_train, X_test, y_train, y_test = pipeline.process_pipeline()

print("Pipeline completed successfully")
print("X_train:", X_train.shape)
print("X_test:", X_test.shape)