import pandas as pd

# Input weather data
input_path = "data/processed/weather_grid_weather.csv"

# Output feature data
output_path = "data/processed/weather_features.csv"

# Load data
df = pd.read_csv(input_path)

print("Rows:", len(df))
print("\nColumns:")
print(df.columns.tolist())

# Convert datetime
df["datetime"] = pd.to_datetime(df["datetime"])

# Sort by location and time
df = df.sort_values(["latitude", "longitude", "datetime"])

# Rolling rainfall over previous 6 hours
df["rainfall_6h"] = (
    df.groupby(["latitude", "longitude"])["rainfall_mm"]
    .rolling(6, min_periods=1)
    .sum()
    .reset_index(level=[0, 1], drop=True)
)

# Rolling rainfall over previous 24 hours
df["rainfall_24h"] = (
    df.groupby(["latitude", "longitude"])["rainfall_mm"]
    .rolling(24, min_periods=1)
    .sum()
    .reset_index(level=[0, 1], drop=True)
)

# Heat indicator
df["heat_indicator"] = (
    (df["temperature_c"] >= 35) &
    (df["humidity_pct"] >= 60)
).astype(int)

# Heavy rainfall indicator
df["heavy_rain_indicator"] = (
    df["rainfall_6h"] >= 50
).astype(int)

# Save
df.to_csv(output_path, index=False)

print("\nDONE!")
print("Saved to:", output_path)
print("Rows:", len(df))
print("\nPreview:")
print(df.head())