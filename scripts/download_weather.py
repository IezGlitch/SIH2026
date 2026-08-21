import requests
import pandas as pd

# Katihar - temporary test coordinate
latitude = 25.53
longitude = 87.58

url = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": latitude,
    "longitude": longitude,
    "start_date": "2026-06-25",
    "end_date": "2026-06-26",
    "hourly": "temperature_2m,relative_humidity_2m,precipitation",
    "timezone": "Asia/Kolkata"
}

response = requests.get(url, params=params)

print("Status code:", response.status_code)

data = response.json()

df = pd.DataFrame({
    "datetime": data["hourly"]["time"],
    "temperature_c": data["hourly"]["temperature_2m"],
    "humidity_pct": data["hourly"]["relative_humidity_2m"],
    "rainfall_mm": data["hourly"]["precipitation"]
})

print(df.head())
print("\nTotal rows:", len(df))
output_path = "data/raw/katihar/katihar_weather_test.csv"

df.to_csv(output_path, index=False)

print(f"\nSaved to: {output_path}")