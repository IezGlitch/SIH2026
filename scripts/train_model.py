import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
import joblib

INPUT = "data/processed/ml_ready_dataset.csv"
MODEL_PATH = "models/flood_risk_model.pkl"

print("Loading ML dataset...")

df = pd.read_csv(INPUT)

# --------------------------------------------------
# Target
# --------------------------------------------------

target = "flood_target"

if target not in df.columns:
    raise ValueError("flood_target column not found.")

# --------------------------------------------------
# Select useful numeric features
# --------------------------------------------------

candidate_features = [
    "temperature_c",
    "humidity_pct",
    "rainfall_mm",
    "rainfall_6h_mm",
    "rainfall_24h_mm",
    "temperature_6h_avg",
    "humidity_6h_avg",
    "heat_risk",
    "rainfall_risk",
    "rainfall_intensity",
    "humidity_rain_index",
    "flood_pressure_index",
    "hour",
    "day",
    "month"
]

features = [
    col for col in candidate_features
    if col in df.columns
]

print("\nFeatures used:")
print(features)

X = df[features].copy()
y = df[target].astype(int)

# --------------------------------------------------
# Remove invalid rows
# --------------------------------------------------

valid = y.notna()

X = X.loc[valid]
y = y.loc[valid]

# --------------------------------------------------
# Check target
# --------------------------------------------------

print("\nTarget distribution:")
print(y.value_counts())

if y.nunique() < 2:
    raise ValueError(
        "Only one target class exists. "
        "More labelled flood/non-flood data is required."
    )

# --------------------------------------------------
# Train / test split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining rows:", len(X_train))
print("Testing rows:", len(X_test))

# --------------------------------------------------
# Model pipeline
# --------------------------------------------------

model = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="median")
    ),
    (
        "classifier",
        RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced",
            max_depth=10
        )
    )
])

# --------------------------------------------------
# Train
# --------------------------------------------------

print("\nTraining Random Forest...")

model.fit(
    X_train,
    y_train
)

# --------------------------------------------------
# Evaluate
# --------------------------------------------------

predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)

print("\n==============================")
print("MODEL RESULTS")
print("==============================")

print("Accuracy:", round(accuracy, 4))

print("\nClassification report:")
print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)

# --------------------------------------------------
# Feature importance
# --------------------------------------------------

classifier = model.named_steps["classifier"]

importance = pd.DataFrame({
    "feature": features,
    "importance": classifier.feature_importances_
}).sort_values(
    "importance",
    ascending=False
)

print("\nFeature importance:")
print(importance.to_string(index=False))

# --------------------------------------------------
# Save model
# --------------------------------------------------

Path("models").mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_PATH
)

print("\nModel saved:")
print(MODEL_PATH)

print("\nDONE!")