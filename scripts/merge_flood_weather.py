import pandas as pd
from pathlib import Path


# =========================
# FILES
# =========================

flood_file = "data/processed/flood_master.csv"
weather_file = "data/processed/district_weather.csv"
target_file = "data/processed/target_districts.csv"

out_file = "data/processed/flood_weather_master.csv"


# =========================
# CLEAN DISTRICT NAMES
# =========================

def clean_name(x):
    if pd.isna(x):
        return ""

    x = str(x).lower().strip()

    # remove common words
    x = x.replace(" district", "")
    x = x.replace(" dist", "")

    # normalize punctuation
    for ch in ["-", "_", ",", ".", "'", '"']:
        x = x.replace(ch, " ")

    # remove extra spaces
    x = " ".join(x.split())

    return x


# =========================
# LOAD DATA
# =========================

print("\nLoading data...")

flood = pd.read_csv(flood_file)
weather = pd.read_csv(weather_file)

print("Flood rows:", len(flood))
print("Weather rows:", len(weather))


# =========================
# FLOOD DISTRICT KEY
# =========================

flood["district_key"] = flood["district_key"].apply(clean_name)


# =========================
# CONVERT WEATHER GID → DISTRICT NAME
# =========================

print("\nMapping weather GIDs to district names...")
# GID → district name mapping
gid_to_name = {
    "IND.5.10_1": "Gaya",
    "IND.5.5_1": "Begusarai",
    "IND.5.15_1": "Katihar"
}

weather["district_name"] = (
    weather["district"]
    .astype(str)
    .str.strip()
    .map(gid_to_name)
)

weather["district_key"] = weather["district_name"].apply(clean_name)



# =========================
# CHECK MAPPING
# =========================

print("\nWeather districts mapped:")

print(
    weather[["district", "district_name", "district_key"]]
    .drop_duplicates()
    .to_string(index=False)
)


# =========================
# CONVERT WEATHER VALUES
# =========================

for col in ["temperature_c", "humidity_pct", "rainfall_mm"]:
    weather[col] = pd.to_numeric(
        weather[col],
        errors="coerce"
    )


# =========================
# WEATHER SUMMARY BY DISTRICT
# =========================

print("\nCreating weather summary...")

weather_summary = (
    weather
    .groupby("district_key", as_index=False)
    .agg(
        avg_temperature_c=("temperature_c", "mean"),
        avg_humidity_pct=("humidity_pct", "mean"),
        total_rainfall_mm=("rainfall_mm", "sum")
    )
)


# =========================
# MERGE FLOOD + WEATHER
# =========================

print("\nMerging flood and weather data...")

final = flood.merge(
    weather_summary,
    on="district_key",
    how="left"
)


# =========================
# SAVE
# =========================

Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)

final.to_csv(
    out_file,
    index=False
)


# =========================
# FINAL CHECK
# =========================

print("\n==============================")
print("DONE!")
print("==============================")

print("Final dataset:", final.shape)
print("Saved:", out_file)

print(
    "Flood rows with weather:",
    final["avg_temperature_c"].notna().sum()
)

print(
    "Districts with weather:",
    final.loc[
        final["avg_temperature_c"].notna(),
        "district_key"
    ].nunique()
)

print("\nWeather summary:")
print(weather_summary.to_string(index=False))