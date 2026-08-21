import xarray as xr
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.transform import from_bounds
from rasterio.mask import mask
from scipy.interpolate import griddata

gdf = gpd.read_file("target_districts.geojson")

tasks = [
    ("Katihar", r"data\Katihar\katihar_sentinel3_lst_20260709\S3A_SL_2_LST____20260709T155342_20260709T155642_20260711T061809_0179_141_254_0360_PS1_O_NT_005.SEN3"),
    ("Begusarai", r"data\Begusarai\begusarai_sentinel3_lst_20260713\S3A_SL_2_LST____20260713T154957_20260713T155257_20260715T083713_0179_141_311_0360_PS1_O_NT_005.SEN3"),
]

for district, base in tasks:
    print(f"\n--- {district} ---")
    lst_ds = xr.open_dataset(f"{base}\\LST_in.nc")
    geo_ds = xr.open_dataset(f"{base}\\geodetic_in.nc")

    lst = lst_ds["LST"].values
    lat = geo_ds["latitude_in"].values
    lon = geo_ds["longitude_in"].values

    row = gdf[gdf["NAME_2"] == district]
    minx, miny, maxx, maxy = row.total_bounds
    print(f"{district} bounds: {minx}, {miny}, {maxx}, {maxy}")

    res = 0.01
    out_width = int((maxx - minx) / res)
    out_height = int((maxy - miny) / res)
    grid_x, grid_y = np.meshgrid(
        np.linspace(minx, maxx, out_width),
        np.linspace(maxy, miny, out_height)
    )

    points = np.column_stack((lon.flatten(), lat.flatten()))
    values = lst.flatten()
    valid = ~np.isnan(values)

    gridded_lst = griddata(points[valid], values[valid], (grid_x, grid_y), method="linear")

    transform = from_bounds(minx, miny, maxx, maxy, out_width, out_height)
    gridded_path = f"data/{district}/{district.lower()}_sentinel3_lst_gridded.tiff"

    with rasterio.open(
        gridded_path, "w",
        driver="GTiff", height=out_height, width=out_width, count=1,
        dtype="float32", crs="EPSG:4326", transform=transform
    ) as dst:
        dst.write(gridded_lst.astype("float32"), 1)

    with rasterio.open(gridded_path) as src:
        geoms = [row.geometry.iloc[0].__geo_interface__]
        out_image, out_transform = mask(src, geoms, crop=True, nodata=np.nan)
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff", "height": out_image.shape[1],
            "width": out_image.shape[2], "transform": out_transform
        })

        clipped_path = f"data/{district}/{district.lower()}_sentinel3_lst_clipped.tiff"
        with rasterio.open(clipped_path, "w", **out_meta) as dst:
            dst.write(out_image)

    valid_vals = out_image[0][~np.isnan(out_image[0])]
    if len(valid_vals) > 0:
        print(f"Clipped: {out_image.shape[2]}x{out_image.shape[1]}, LST range: {valid_vals.min()-273.15:.1f}C to {valid_vals.max()-273.15:.1f}C")
    else:
        print("WARNING: no valid LST pixels after clipping")

print("\nAll done.")