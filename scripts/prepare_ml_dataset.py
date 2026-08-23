import pandas as pd
import numpy as np

INPUT = "data/processed/final_weather_flood_dataset.csv"
OUTPUT = "data/processed/ml_ready_dataset.csv"

print("Loading final dataset...")

df = pd.read_csv(INPUT)

# --------------------------------------------------
# 1. Clean column names
# --------------------------------------------------
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# --------------------------------------------------
# 2. Convert datetime
# --------------------------------------------------
if "datetime" in df.columns:
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

# --------------------------------------------------
# 3. Create useful time features
# --------------------------------------------------
if "datetime" in df.columns:
    df["hour"] = df["datetime"].dt.hour
    df["day"] = df["datetime"].dt.day
    df["month"] = df["datetime"].dt.month

# --------------------------------------------------
# 4. Convert important numeric columns
# --------------------------------------------------
numeric_candidates = [
    "temperature_c",
    "humidity_pct",
    "rainfall_mm",
    "rainfall_6h_mm",
    "rainfall_24h_mm",
    "rainfall_6h_avg",
    "rainfall_24h_avg",
    "heat_risk",
    "flood_risk",
    "flood_events",
    "mean_flood_duration",
    "population",
    "permanent_water",
    "corrected_percent_flooded_area",
    "percent_flooded_area"
]

for col in numeric_candidates:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# --------------------------------------------------
# 5. Create flood target
# --------------------------------------------------
# 1 = flood/risk event
# 0 = normal/low risk

if "weather_risk_level" in df.columns:
    df["flood_target"] = (
        df["weather_risk_level"]
        .astype(str)
        .str.upper()
        .isin(["MODERATE", "HIGH"])
    ).astype(int)

elif "flood_events" in df.columns:
    df["flood_target"] = (
        pd.to_numeric(df["flood_events"], errors="coerce")
        .fillna(0) > 0
    ).astype(int)

else:
    raise ValueError(
        "No suitable flood target column found."
    )

# --------------------------------------------------
# 6. Create rainfall intensity feature
# --------------------------------------------------
if "rainfall_24h_mm" in df.columns:
    df["rainfall_intensity"] = (
        df["rainfall_24h_mm"] / 24
    )

elif "rainfall_mm" in df.columns:
    df["rainfall_intensity"] = df["rainfall_mm"]

# --------------------------------------------------
# 7. Create humidity-rain interaction
# --------------------------------------------------
if "humidity_pct" in df.columns and "rainfall_24h_mm" in df.columns:
    df["humidity_rain_index"] = (
        df["humidity_pct"] * df["rainfall_24h_mm"] / 100
    )

# --------------------------------------------------
# 8. Create flood-pressure indicators
# --------------------------------------------------
if (
    "rainfall_24h_mm" in df.columns
    and "corrected_percent_flooded_area" in df.columns
):
    df["flood_pressure_index"] = (
        df["rainfall_24h_mm"]
        * df["corrected_percent_flooded_area"]
    )

# --------------------------------------------------
# 9. Remove rows without target
# --------------------------------------------------
df = df.dropna(subset=["flood_target"])

# --------------------------------------------------
# 10. Replace infinite values
# --------------------------------------------------
df = df.replace([np.inf, -np.inf], np.nan)

# --------------------------------------------------
# 11. Save ML-ready dataset
# --------------------------------------------------
df.to_csv(OUTPUT, index=False)

# --------------------------------------------------
# 12. Final information
# --------------------------------------------------
print("\nML DATASET CREATED!")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Saved:", OUTPUT)

print("\nTARGET DISTRIBUTION:")
print(df["flood_target"].value_counts())

print("\nFEATURE COLUMNS:")
print(df.columns.tolist())

print("\nDONE!")