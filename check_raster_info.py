import rasterio

input_raster = r"data\Katihar\katihar_sentinel1_sample\S1D_IW_GRDH_1SDV_20260706T121245_20260706T121310_003553_0064F5_E3F2_COG.SAFE\measurement\s1d-iw-grd-vh-20260706t121245-20260706t121310-003553-0064f5-002-cog.tiff"

with rasterio.open(input_raster) as src:
    print("CRS:", src.crs)
    print("Transform:", src.transform)
    print("Number of GCPs:", len(src.gcps[0]) if src.gcps else 0)
    print("GCP CRS:", src.gcps[1] if src.gcps else None)
    if src.gcps and len(src.gcps[0]) > 0:
        print("Sample GCP:", src.gcps[0][0])