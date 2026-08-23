import pandas as pd
from pathlib import Path

print("\nLoading weather data...")

# ============================================================
# 1. FILE PATHS
# ============================================================

input_path = "data/processed/district_weather.csv"
output_path = "data/processed/weather_features.csv"

# ============================================================
# 2. LOAD DATA
# ============================================================

df = pd.read_csv(input_path)

print("Original rows:", len(df))
print("Original columns:")
print(df.columns.tolist())

# ============================================================
# 3. WEATHER GID -> DISTRICT NAME
# ============================================================

gid_to_name = {
    "IND.5.10_1": "Gaya",
    "IND.5.5_1": "Begusarai",
    "IND.5.15_1": "Katihar"
}

# ============================================================
# 4. CHECK WEATHER GIDs
# ============================================================

print("\nWEATHER GIDs:")

if "district" not in df.columns:
    raise KeyError(
        "Column 'district' not found in district_weather.csv"
    )

print(
    df["district"]
    .dropna()
    .unique()
)

# ============================================================
# 5. MAP GID -> DISTRICT NAME
# ============================================================

df["district_name"] = (
    df["district"]
    .astype(str)
    .str.strip()
    .map(gid_to_name)
)

# Create clean key for merging
df["district_key"] = (
    df["district_name"]
    .str.lower()
    .str.replace(" ", "", regex=False)
)

# ============================================================
# 6. REMOVE UNMAPPED REGIONS
# ============================================================

df = df[
    df["district_name"].notna()
].copy()

print("\nDISTRICTS FOUND:")

print(
    df["district_name"]
    .dropna()
    .unique()
)

print("\nRows after region filtering:", len(df))

# ============================================================
# 7. DATETIME
# ============================================================

df["datetime"] = pd.to_datetime(
    df["datetime"],
    errors="coerce"
)

df = df.dropna(
    subset=["datetime"]
).copy()

df = df.sort_values(
    ["district_key", "datetime"]
).reset_index(drop=True)

# ============================================================
# 8. CONVERT WEATHER VALUES TO NUMERIC
# ============================================================

for col in [
    "temperature_c",
    "humidity_pct",
    "rainfall_mm"
]:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# ============================================================
# 9. RAINFALL FEATURES
# ============================================================

print("\nCreating rainfall features...")

df["rainfall_6h_mm"] = (
    df.groupby("district_key")["rainfall_mm"]
    .transform(
        lambda x:
        x.rolling(
            window=6,
            min_periods=1
        ).sum()
    )
)

df["rainfall_24h_mm"] = (
    df.groupby("district_key")["rainfall_mm"]
    .transform(
        lambda x:
        x.rolling(
            window=24,
            min_periods=1
        ).sum()
    )
)

# ============================================================
# 10. TEMPERATURE FEATURES
# ============================================================

print("Creating temperature features...")

df["temperature_6h_avg"] = (
    df.groupby("district_key")["temperature_c"]
    .transform(
        lambda x:
        x.rolling(
            window=6,
            min_periods=1
        ).mean()
    )
)

# ============================================================
# 11. HUMIDITY FEATURES
# ============================================================

print("Creating humidity features...")

df["humidity_6h_avg"] = (
    df.groupby("district_key")["humidity_pct"]
    .transform(
        lambda x:
        x.rolling(
            window=6,
            min_periods=1
        ).mean()
    )
)

# ============================================================
# 12. HEAT RISK
# ============================================================

print("Creating heat risk...")

df["heat_risk"] = (
    (df["temperature_c"] >= 35) &
    (df["humidity_pct"] >= 60)
).astype(int)

# ============================================================
# 13. RAINFALL RISK
# ============================================================

print("Creating rainfall risk...")

df["rainfall_risk"] = (
    (df["rainfall_6h_mm"] >= 20) |
    (df["rainfall_24h_mm"] >= 50)
).astype(int)

# ============================================================
# 14. FINAL WEATHER DATASET
# ============================================================

feature_columns = [
    "district_key",
    "district_name",
    "datetime",
    "temperature_c",
    "humidity_pct",
    "rainfall_mm",
    "rainfall_6h_mm",
    "rainfall_24h_mm",
    "temperature_6h_avg",
    "humidity_6h_avg",
    "heat_risk",
    "rainfall_risk"
]

features = df[feature_columns].copy()

# ============================================================
# 15. SAVE
# ============================================================

Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)

features.to_csv(
    output_path,
    index=False
)

# ============================================================
# 16. FINAL OUTPUT
# ============================================================

print("\n==============================")
print("WEATHER FEATURES CREATED")
print("==============================")

print("\nFinal rows:", len(features))

print("\nDistrict counts:")

print(
    features["district_name"]
    .value_counts()
)

print("\nFinal columns:")

print(
    features.columns.tolist()
)

print("\nSaved:")

print(output_path)

print("\nSample:")

print(
    features.head(10)
    .to_string(index=False)
)

print("\nDONE!")