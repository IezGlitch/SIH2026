import rasterio
import matplotlib.pyplot as plt
import numpy as np

with rasterio.open(r"data\Katihar\katihar_sentinel1_clipped.tiff") as src:
    band1 = src.read(1)
    # Clip extreme values for better visualization (SAR data has huge dynamic range)
    band1 = np.clip(band1, 0, np.percentile(band1[band1 > 0], 99))

plt.figure(figsize=(10, 8))
plt.imshow(band1, cmap="gray")
plt.title("Katihar Sentinel-1 VH - Clipped to district boundary")
plt.colorbar(label="Backscatter intensity")
plt.savefig("data/Katihar/katihar_clip_preview.png", dpi=150)
print("Preview saved to data/Katihar/katihar_clip_preview.png")