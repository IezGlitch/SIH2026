import geopandas as gpd
import rasterio
from rasterio.mask import mask
import os

gdf = gpd.read_file("target_districts.geojson")
bands = ["B02", "B03", "B04", "B08"]

# (district, base_folder_path, date_prefix, tile_id, output_subfolder)
tasks = [
    ("Gaya", r"data\Gaya\gaya_sentinel2_sample\S2C_MSIL2A_20260524T045701_N0512_R119_T44RRN_20260524T095301.SAFE\GRANULE\L2A_T44RRN_A008955_20260524T050741\IMG_DATA\R10m", "T44RRN_20260524T045701", "gaya_s2"),
    ("Begusarai", r"data\Begusarai\begusarai_sentinel2_sample\S2C_MSIL2A_20260710T044701_N0512_R076_T45RUH_20260710T095809.SAFE\GRANULE\L2A_T45RUH_A009627_20260710T045042\IMG_DATA\R10m", "T45RUH_20260710T044701", "begusarai_s2_RUH"),
    ("Begusarai", r"data\Begusarai\begusarai_sentinel2_T45RVH\S2C_MSIL2A_20260710T044701_N0512_R076_T45RVH_20260710T095809.SAFE\GRANULE\L2A_T45RVH_A009627_20260710T045042\IMG_DATA\R10m", "T45RVH_20260710T044701", "begusarai_s2_RVH"),
    ("Begusarai", r"data\Begusarai\begusarai_sentinel2_T45RUJ\S2C_MSIL2A_20260710T044701_N0512_R076_T45RUJ_20260710T095809.SAFE\GRANULE\L2A_T45RUJ_A009627_20260710T045042\IMG_DATA\R10m", "T45RUJ_20260710T044701", "begusarai_s2_RUJ"),
    ("Begusarai", r"data\Begusarai\begusarai_sentinel2_T45RVJ\S2C_MSIL2A_20260710T044701_N0512_R076_T45RVJ_20260710T095809.SAFE\GRANULE\L2A_T45RVJ_A009627_20260710T045042\IMG_DATA\R10m", "T45RVJ_20260710T044701", "begusarai_s2_RVJ"),
]

for district, base, prefix, out_prefix in tasks:
    row = gdf[gdf["NAME_2"] == district]
    out_dir = f"data/{district}/clipped_sentinel2"
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n--- {out_prefix} ---")
    for band in bands:
        input_path = f"{base}\\{prefix}_{band}_10m.jp2"
        output_path = f"{out_dir}/{out_prefix}_{band}_clipped.tiff"

        if not os.path.exists(input_path):
            print(f"  SKIPPED (not found): {input_path}")
            continue

        with rasterio.open(input_path) as src:
            reprojected = row.to_crs(src.crs)
            geoms = [reprojected.geometry.iloc[0].__geo_interface__]

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

            print(f"  {band}: {src.width}x{src.height} -> {out_image.shape[2]}x{out_image.shape[1]}")

print("\nAll done.")