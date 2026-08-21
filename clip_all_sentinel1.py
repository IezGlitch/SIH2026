import geopandas as gpd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
import os

def georeference_and_clip(input_raster, district_polygon, georeferenced_path, clipped_path):
    with rasterio.open(input_raster) as src:
        if src.crs is None and src.gcps[0]:
            gcps, gcp_crs = src.gcps
            print(f"  Using {len(gcps)} GCPs to georeference...")

            transform, width, height = calculate_default_transform(
                gcp_crs, gcp_crs, src.width, src.height, gcps=gcps
            )
            kwargs = src.meta.copy()
            kwargs.update({"crs": gcp_crs, "transform": transform, "width": width, "height": height})

            with rasterio.open(georeferenced_path, "w", **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_crs=gcp_crs,
                        gcps=gcps,
                        dst_transform=transform,
                        dst_crs=gcp_crs,
                        resampling=Resampling.nearest
                    )
        else:
            # Already has a proper CRS, just copy it as-is for the next step
            georeferenced_path = input_raster

    with rasterio.open(georeferenced_path) as src:
        polygon_reprojected = district_polygon.to_crs(src.crs)
        geoms = [polygon_reprojected.geometry.iloc[0].__geo_interface__]

        out_image, out_transform = mask(src, geoms, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        with rasterio.open(clipped_path, "w", **out_meta) as dst:
            dst.write(out_image)

        print(f"  Clipped: {out_image.shape[2]} x {out_image.shape[1]} -> {clipped_path}")


gdf = gpd.read_file("target_districts.geojson")

# List every raster we want clipped: (district, input_path, output_name)
tasks = [
    ("Katihar", r"data\Katihar\katihar_sentinel1_sample\S1D_IW_GRDH_1SDV_20260706T121245_20260706T121310_003553_0064F5_E3F2_COG.SAFE\measurement\s1d-iw-grd-vh-20260706t121245-20260706t121310-003553-0064f5-002-cog.tiff", "katihar_sentinel1_vh"),
    ("Begusarai", r"data\Begusarai\begusarai_sentinel1_sample\S1D_IW_GRDH_1SDV_20260714T001125_20260714T001150_003662_00689F_AEA9_COG.SAFE\measurement\s1d-iw-grd-vh-20260714t001125-20260714t001150-003662-00689f-002-cog.tiff", "begusarai_sentinel1_flood_vh"),
    ("Begusarai", r"data\Begusarai\begusarai_sentinel1_preflood_20260702\S1D_IW_GRDH_1SDV_20260702T001124_20260702T001149_003487_0062AB_FE92_COG.SAFE\measurement\s1d-iw-grd-vh-20260702t001124-20260702t001149-003487-0062ab-002-cog.tiff", "begusarai_sentinel1_preflood_vh"),
    ("Gaya", r"data\Gaya\gaya_sentinel1_sample\S1A_IW_GRDH_1SDV_20260520T001231_20260520T001256_064593_0822ED_151E_COG.SAFE\measurement\s1a-iw-grd-vh-20260520t001231-20260520t001256-064593-0822ed-002-cog.tiff", "gaya_sentinel1_vh"),
]

for district, input_path, output_name in tasks:
    print(f"\nProcessing {output_name}...")
    if not os.path.exists(input_path):
        print(f"  SKIPPED - file not found: {input_path}")
        continue

    row = gdf[gdf["NAME_2"] == district]
    out_dir = f"data/{district}"
    georef_path = f"{out_dir}/{output_name}_georeferenced.tiff"
    clip_path = f"{out_dir}/{output_name}_clipped.tiff"

    georeference_and_clip(input_path, row, georef_path, clip_path)

print("\nAll done.")