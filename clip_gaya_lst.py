import geopandas as gpd
import rasterio
from rasterio.mask import mask
import matplotlib.pyplot as plt
import numpy as np

gdf = gpd.read_file("target_districts.geojson")
gaya = gdf[gdf["NAME_2"] == "Gaya"]

with rasterio.open("data/Gaya/gaya_sentinel3_lst_gridded.tiff") as src:
    geoms = [gaya.geometry.iloc[0].__geo_interface__]
    out_image, out_transform = mask(src, geoms, crop=True, nodata=np.nan)
    out_meta = src.meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform
    })

    with rasterio.open("data/Gaya/gaya_sentinel3_lst_clipped.tiff", "w", **out_meta) as dst:
        dst.write(out_image)

print(f"Clipped LST: {out_image.shape[2]} x {out_image.shape[1]}")

lst_data = out_image[0]
valid = lst_data[~np.isnan(lst_data)]
print(f"LST value range: {valid.min():.1f}K to {valid.max():.1f}K")
print(f"LST value range: {valid.min()-273.15:.1f}C to {valid.max()-273.15:.1f}C")

plt.figure(figsize=(8, 8))
plt.imshow(lst_data, cmap="inferno")
plt.title("Gaya Land Surface Temperature (May 24, 2026)")
plt.colorbar(label="Temperature (K)")
plt.savefig("data/Gaya/gaya_lst_preview.png", dpi=150)
print("Preview saved to data/Gaya/gaya_lst_preview.png")