import geopandas as gpd
import numpy as np
import pandas as pd

# Load target districts
gdf = gpd.read_file("target_districts.geojson")

# Get the combined boundary of all 3 districts
boundary = gdf.geometry.union_all()

# Create a regular grid of points
minx, miny, maxx, maxy = boundary.bounds

step = 0.05   # roughly 5 km

points = []

for lon in np.arange(minx, maxx, step):
    for lat in np.arange(miny, maxy, step):
        if boundary.contains(
            gpd.points_from_xy([lon], [lat])[0]
        ):
            points.append((lon, lat))

# Save grid
grid = pd.DataFrame(points, columns=["longitude", "latitude"])

grid.to_csv(
    "data/processed/weather_grid.csv",
    index=False
)

print("Grid points:", len(grid))
print(grid.head())
print("\nSaved to data/processed/weather_grid.csv")