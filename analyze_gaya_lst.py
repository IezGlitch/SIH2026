import rasterio
import numpy as np
import csv

INPUT_TIFF = "data/Gaya/gaya_sentinel3_lst_clipped.tiff"
HEAT_RISK_TIFF = "data/Gaya/gaya_heat_risk.tif"
STATS_CSV = "data/Gaya/gaya_lst_statistics.csv"

THRESHOLDS = {
    "Low":      (-np.inf, 35),
    "Moderate": (35, 40),
    "High":     (40, 45),
    "Extreme":  (45, np.inf),
}

with rasterio.open(INPUT_TIFF) as src:
    lst_kelvin = src.read(1).astype(float)
    profile = src.profile
    nodata = src.nodata

if nodata is not None:
    valid_mask = lst_kelvin != nodata
else:
    valid_mask = ~np.isnan(lst_kelvin)

lst_celsius = lst_kelvin - 273.15
lst_celsius[~valid_mask] = np.nan

valid_values = lst_celsius[valid_mask]
min_lst = np.nanmin(valid_values)
max_lst = np.nanmax(valid_values)
mean_lst = np.nanmean(valid_values)
total_valid_pixels = valid_values.size

print(f"Min LST: {min_lst:.2f} C")
print(f"Max LST: {max_lst:.2f} C")
print(f"Mean LST: {mean_lst:.2f} C")
print(f"Total valid pixels: {total_valid_pixels}")

heat_class = np.full(lst_celsius.shape, 0, dtype=np.uint8)
category_codes = {"Low": 1, "Moderate": 2, "High": 3, "Extreme": 4}

category_stats = []
for name, (low, high) in THRESHOLDS.items():
    mask = valid_mask & (lst_celsius >= low) & (lst_celsius < high)
    count = np.sum(mask)
    pct = (count / total_valid_pixels) * 100 if total_valid_pixels > 0 else 0
    heat_class[mask] = category_codes[name]
    category_stats.append((name, count, pct))
    print(f"{name} ({low} to {high} C): {count} pixels, {pct:.2f}% of area")

out_profile = profile.copy()
out_profile.update(dtype=rasterio.uint8, count=1, nodata=0)

with rasterio.open(HEAT_RISK_TIFF, "w", **out_profile) as dst:
    dst.write(heat_class, 1)

print(f"\nHeat risk raster saved to {HEAT_RISK_TIFF}")

with open(STATS_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Min LST (C)", f"{min_lst:.2f}"])
    writer.writerow(["Max LST (C)", f"{max_lst:.2f}"])
    writer.writerow(["Mean LST (C)", f"{mean_lst:.2f}"])
    writer.writerow(["Total valid pixels", total_valid_pixels])
    writer.writerow([])
    writer.writerow(["Category", "Pixel Count", "Percent Area (%)"])
    for name, count, pct in category_stats:
        writer.writerow([name, count, f"{pct:.2f}"])

print(f"Statistics CSV saved to {STATS_CSV}")