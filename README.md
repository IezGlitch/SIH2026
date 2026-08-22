# SIH2026 – Gaya Heatwave LST Analysis

## Objective
- Extract Sentinel-3 LST data for Gaya district
- Cover heatwave event window: 10–25 May 2026
- Convert satellite data into readable temperature map
- Analyze heat risk across the district

## Environment Setup
- Created `.env` file for CDSE login credentials
- Added `.gitignore` to keep credentials private
- Installed required libraries: xarray, netCDF4, rasterio, geopandas, numpy

## Product Identification & Download
- Searched CDSE for correct Sentinel-3 SLSTR LST product
- Verified product covers Gaya during heatwave window
- Downloaded product as `.zip` file
- Extracted `.SEN3` folder containing:
  - `LST_in.nc` → temperature values
  - `geodetic_in.nc` → pixel coordinates
  - `flags_in.nc` → quality flags

## Data Inspection
- Explored internal structure of LST NetCDF file
- Confirmed product type, resolution, acquisition time

## District Boundary Preparation
- Downloaded GADM Level-2 district boundary data for India
- Filtered out Gaya, Katihar, Begusarai boundaries
- Saved as `target_districts.geojson`

## Gridding & Clipping
- Converted scattered satellite data into proper grid (GeoTIFF)
- Clipped raster to exact Gaya district boundary
- Generated:
  - `gaya_sentinel3_lst_clipped.tiff` → final LST raster
  - `gaya_lst_preview.png` → visual preview

## Statistical Analysis
- Converted temperature from Kelvin to Celsius
- Calculated min, max, mean LST
- Classified area into heat categories:
  - Low (<35°C)
  - Moderate (35–40°C)
  - High (40–45°C)
  - Extreme (>45°C)
- Generated:
  - `gaya_heat_risk.tif` → classified heat-risk map
  - `gaya_lst_statistics.csv` → statistics table

## Key Findings
- Min LST: 12.06°C
- Max LST: 32.63°C
- Mean LST: 28.02°C
- 100% area falls under "Low" category
- Note: data is from a nighttime satellite pass — daytime data needed for true heatwave peak analysis

## Final Deliverables
- `gaya_sentinel3_lst_clipped.tiff` — LST raster
- `gaya_heat_risk.tif` — heat risk map
- `gaya_lst_preview.png` — visual preview
- `gaya_lst_statistics.csv` — statistics

## Tools Used
- Python, xarray, netCDF4, rasterio, geopandas, numpy
- Git & GitHub for version control
