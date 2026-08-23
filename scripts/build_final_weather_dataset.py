import pandas as pd
from pathlib import Path

WEATHER = "data/processed/weather_features.csv"
FLOOD = "data/processed/flood_master.csv"
OUTPUT = "data/processed/final_weather_flood_dataset.csv"

TARGET_REGIONS = ["begusarai", "gaya", "katihar"]

print("\nLoading data...")

weather = pd.read_csv(WEATHER)
flood = pd.read_csv(FLOOD)

# Clean keys
weather["district_key"] = (
    weather["district_key"].astype(str).str.lower().str.strip()
)

flood["district_key"] = (
    flood["district_key"].astype(str).str.lower().str.strip()
)

# Keep only regions for which we have weather data
weather = weather[
    weather["district_key"].isin(TARGET_REGIONS)
].copy()

flood = flood[
    flood["district_key"].isin(TARGET_REGIONS)
].copy()

print("\nWEATHER:")
print("Rows:", len(weather))
print(weather["district_key"].value_counts())

print("\nFLOOD:")
print("Rows:", len(flood))
print(flood["district_key"].value_counts())

# ------------------------------------------------------------
# FLOOD DATA IS DISTRICT LEVEL
# Keep one flood record for each target district
# ------------------------------------------------------------

flood = flood.drop_duplicates(
    subset=["district_key"]
).copy()

# Avoid duplicate district-name columns
if "district_name" in flood.columns:
    flood = flood.drop(columns=["district_name"])

# ------------------------------------------------------------
# MERGE
# ------------------------------------------------------------

final = weather.merge(
    flood,
    on="district_key",
    how="left"
)

# ------------------------------------------------------------
# WEATHER RISK
# ------------------------------------------------------------

final["overall_weather_risk"] = (
    (final["heat_risk"] == 1) |
    (final["rainfall_risk"] == 1)
).astype(int)

def get_risk(row):
    if row["heat_risk"] == 1 and row["rainfall_risk"] == 1:
        return "HIGH"
    elif row["heat_risk"] == 1 or row["rainfall_risk"] == 1:
        return "MODERATE"
    return "LOW"

final["weather_risk_level"] = final.apply(
    get_risk,
    axis=1
)

# ------------------------------------------------------------
# SAVE
# ------------------------------------------------------------

Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)
# REMOVE DUPLICATE REGION + TIMESTAMP RECORDS
print("\nBefore duplicate removal:", len(final))

final = final.drop_duplicates(
    subset=["district_key", "datetime"],
    keep="first"
).reset_index(drop=True)

print("After duplicate removal:", len(final))
print("Regions:", sorted(final["district_key"].dropna().unique().tolist()))
print("Duplicate region+datetime:", final.duplicated(
    subset=["district_key", "datetime"]
).sum())
final.to_csv(
    OUTPUT,
    index=False
)

# ------------------------------------------------------------
# REPORT
# ------------------------------------------------------------

print("\n================================")
print("FINAL DATASET CREATED")
print("================================")

print("Rows:", len(final))
print("Columns:", len(final.columns))

print("\nRegions:")
print(final["district_key"].value_counts())

print("\nWeather risk:")
print(final["weather_risk_level"].value_counts())

print("\nSaved:")
print(OUTPUT)

print("\nSample:")
print(final.head(10).to_string(index=False))

print("\nDONE!")