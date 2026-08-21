import rasterio

path = r"data\Katihar\katihar_sentinel2_sample\S2C_MSIL2A_20260707T043701_N0512_R033_T45RWJ_20260707T090407.SAFE\GRANULE\L2A_T45RWJ_A009584_20260707T045126\IMG_DATA\R10m\T45RWJ_20260707T043701_B04_10m.jp2"

with rasterio.open(path) as src:
    print("CRS:", src.crs)
    print("Size:", src.width, "x", src.height)
    print("Transform:", src.transform)