import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Input files
weather_path = "data/processed/weather_grid_weather.csv"
district_path = "target_districts.geojson"

# Output
output_path = "data/processed/district_weather.csv"

print("Loading weather data...")
weather = pd.read_csv(weather_path)

print("Loading district boundaries...")
districts = gpd.read_file(district_path)

# Convert weather coordinates into geographic points
geometry = [
    Point(lon, lat)
    for lon, lat in zip(weather["longitude"], weather["latitude"])
]

weather_gdf = gpd.GeoDataFrame(
    weather,
    geometry=geometry,
    crs="EPSG:4326"
)

# Make sure district boundaries use same CRS
districts = districts.to_crs("EPSG:4326")

# Spatial join: assign each weather point to a district
joined = gpd.sjoin(
    weather_gdf,
    districts[["NAME_2", "geometry"]],
    how="left",
    predicate="within"
)

# Rename district column
joined = joined.rename(columns={"NAME_2": "district"})

# Remove geometry/index columns
joined = joined.drop(
    columns=["geometry", "index_right"],
    errors="ignore"
)

# Save
joined.to_csv(output_path, index=False)

print("\nDONE!")
print("Rows:", len(joined))
print("Districts found:")
print(joined["district"].value_counts(dropna=False))
print("Saved to:", output_path)