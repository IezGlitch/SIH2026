import xarray as xr
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.transform import from_bounds
from scipy.interpolate import griddata
from pathlib import Path
base = next(Path("data/Gaya/gaya_sentinel3_lst").glob("*.SEN3"))

lst_ds = xr.open_dataset(f"{base}\\LST_in.nc")
geo_ds = xr.open_dataset(f"{base}\\geodetic_in.nc")

lst = lst_ds["LST"].values
lat = geo_ds["latitude_in"].values
lon = geo_ds["longitude_in"].values

print("LST shape:", lst.shape)
print("Lat shape:", lat.shape)
print("Lon range:", np.nanmin(lon), "to", np.nanmax(lon))
print("Lat range:", np.nanmin(lat), "to", np.nanmax(lat))

# Load Gaya's boundary to get its extent
gdf = gpd.read_file("target_districts.geojson")
gaya = gdf[gdf["NAME_2"] == "Gaya"]
minx, miny, maxx, maxy = gaya.total_bounds
print(f"\nGaya bounds: {minx}, {miny}, {maxx}, {maxy}")

# Build a regular output grid covering Gaya's bounding box at ~1km resolution (SLSTR's native res)
res = 0.01  # roughly 1km in degrees
out_width = int((maxx - minx) / res)
out_height = int((maxy - miny) / res)
grid_x, grid_y = np.meshgrid(
    np.linspace(minx, maxx, out_width),
    np.linspace(maxy, miny, out_height)
)

# Interpolate scattered LST points onto the regular grid
points = np.column_stack((lon.flatten(), lat.flatten()))
values = lst.flatten()
valid = ~np.isnan(values)

gridded_lst = griddata(points[valid], values[valid], (grid_x, grid_y), method="linear")

transform = from_bounds(minx, miny, maxx, maxy, out_width, out_height)

with rasterio.open(
    "data/Gaya/gaya_sentinel3_lst_gridded.tiff", "w",
    driver="GTiff", height=out_height, width=out_width, count=1,
    dtype="float32", crs="EPSG:4326", transform=transform
) as dst:
    dst.write(gridded_lst.astype("float32"), 1)

print("\nGridded LST saved: data/Gaya/gaya_sentinel3_lst_gridded.tiff")