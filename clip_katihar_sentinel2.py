import geopandas as gpd
import rasterio
from rasterio.mask import mask
import os

gdf = gpd.read_file("target_districts.geojson")
katihar = gdf[gdf["NAME_2"] == "Katihar"]

base = r"data\Katihar\katihar_sentinel2_sample\S2C_MSIL2A_20260707T043701_N0512_R033_T45RWJ_20260707T090407.SAFE\GRANULE\L2A_T45RWJ_A009584_20260707T045126\IMG_DATA\R10m"

bands = ["B02", "B03", "B04", "B08"]

os.makedirs("data/Katihar/clipped_sentinel2", exist_ok=True)

for band in bands:
    input_path = f"{base}\\T45RWJ_20260707T043701_{band}_10m.jp2"
    output_path = f"data/Katihar/clipped_sentinel2/katihar_s2_{band}_clipped.tiff"

    with rasterio.open(input_path) as src:
        katihar_reprojected = katihar.to_crs(src.crs)
        geoms = [katihar_reprojected.geometry.iloc[0].__geo_interface__]

        out_image, out_transform = mask(src, geoms, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        with rasterio.open(output_path, "w", **out_meta) as dst:
            dst.write(out_image)

        print(f"{band}: {src.width}x{src.height} -> {out_image.shape[2]}x{out_image.shape[1]} -> {output_path}")

print("\nDone.")