import requests
import pandas as pd
import time
import os

# Read the 359 grid points
grid = pd.read_csv("data/processed/weather_grid.csv")

url = "https://archive-api.open-meteo.com/v1/archive"

all_weather = []

for i, row in grid.iterrows():

    latitude = row["latitude"]
    longitude = row["longitude"]

    print(f"Downloading point {i + 1}/{len(grid)}: {latitude}, {longitude}")

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": "2026-06-25",
        "end_date": "2026-06-26",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation",
        "timezone": "Asia/Kolkata"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        df = pd.DataFrame({
            "latitude": latitude,
            "longitude": longitude,
            "datetime": data["hourly"]["time"],
            "temperature_c": data["hourly"]["temperature_2m"],
            "humidity_pct": data["hourly"]["relative_humidity_2m"],
            "rainfall_mm": data["hourly"]["precipitation"]
        })

        all_weather.append(df)

    except Exception as e:
        print(f"ERROR at point {i}: {e}")

    # Small delay so we don't hit the API too quickly
    time.sleep(0.2)


# Combine all points
weather = pd.concat(all_weather, ignore_index=True)

# Create output folder if needed
os.makedirs("data/processed", exist_ok=True)

# Save combined data
output_path = "data/processed/weather_grid_weather.csv"

weather.to_csv(output_path, index=False)

print("\nDONE!")
print("Total rows:", len(weather))
print("Grid points processed:", weather[["latitude", "longitude"]].drop_duplicates().shape[0])
print("Saved to:", output_path)