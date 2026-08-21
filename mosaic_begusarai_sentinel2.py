import rasterio
from rasterio.merge import merge
import glob

bands = ["B02", "B03", "B04", "B08"]

for band in bands:
    files = glob.glob(f"data/Begusarai/clipped_sentinel2/begusarai_s2_R*_{band}_clipped.tiff")
    print(f"\n{band}: merging {len(files)} tiles: {files}")

    src_files = [rasterio.open(f) for f in files]
    mosaic, out_transform = merge(src_files)

    out_meta = src_files[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_transform
    })

    output_path = f"data/Begusarai/clipped_sentinel2/begusarai_s2_{band}_mosaic.tiff"
    with rasterio.open(output_path, "w", **out_meta) as dst:
        dst.write(mosaic)

    for f in src_files:
        f.close()

    print(f"  Saved: {output_path} ({mosaic.shape[2]}x{mosaic.shape[1]})")

print("\nAll bands mosaicked.")