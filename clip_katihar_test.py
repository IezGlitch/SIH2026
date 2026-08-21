import geopandas as gpd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
import numpy as np

input_raster = r"data\Katihar\katihar_sentinel1_sample\S1D_IW_GRDH_1SDV_20260706T121245_20260706T121310_003553_0064F5_E3F2_COG.SAFE\measurement\s1d-iw-grd-vh-20260706t121245-20260706t121310-003553-0064f5-002-cog.tiff"
georeferenced_raster = r"data\Katihar\katihar_sentinel1_georeferenced.tiff"
clipped_raster = r"data\Katihar\katihar_sentinel1_clipped.tiff"

# Step 1: Use GCPs to georeference the raster
with rasterio.open(input_raster) as src:
    gcps, gcp_crs = src.gcps
    print(f"Using {len(gcps)} GCPs to georeference...")

    transform, width, height = calculate_default_transform(
        gcp_crs, gcp_crs, src.width, src.height, gcps=gcps
    )

    kwargs = src.meta.copy()
    kwargs.update({
        "crs": gcp_crs,
        "transform": transform,
        "width": width,
        "height": height
    })

    with rasterio.open(georeferenced_raster, "w", **kwargs) as dst:
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

print(f"Georeferenced raster saved: {georeferenced_raster}")

# Step 2: Clip the georeferenced raster to Katihar's exact polygon
gdf = gpd.read_file("target_districts.geojson")
katihar = gdf[gdf["NAME_2"] == "Katihar"]

with rasterio.open(georeferenced_raster) as src:
    print("Georeferenced raster CRS:", src.crs)
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

    with rasterio.open(clipped_raster, "w", **out_meta) as dst:
        dst.write(out_image)

    print(f"\nClipped raster saved: {clipped_raster}")
    print(f"Georeferenced size: {src.width} x {src.height}")
    print(f"Clipped size: {out_image.shape[2]} x {out_image.shape[1]}")