# **Data Ingestion Pipeline — Mitali**
This covers my part of SOAIDEATHON-S6: fetching raw Sentinel-1, Sentinel-2, and Sentinel-3 satellite imagery from the Copernicus Data Space Ecosystem (CDSE) for our 3 target districts, and preprocessing it toward analysis-ready form.

## **What I built**
An end-to-end pipeline that:
1. Takes India's official district boundaries (GADM) and filters them down to our 3 target districts
2. Authenticates with CDSE (OAuth)
3. Searches CDSE's catalogue for Sentinel-1/2/3 products covering each district during a specific real-world event window
4. Downloads the actual satellite files, with retry/resume logic for unstable connections
5. Georeferences raw Sentinel-1 rasters using their embedded Ground Control Points (GCPs), then clips them to each district's exact polygon boundary
6. Clips Sentinel-2 optical bands (B02, B03, B04, B08) to each district's exact boundary, and mosaics multiple tiles together where one tile alone doesn't give full coverage
7. Converts Sentinel-3 scattered-swath LST (Land Surface Temperature) data into a proper gridded raster, then clips it to each district's exact boundary
8. Organizes everything into a clean folder structure for the rest of the team

## **Target districts**
I picked 3 Bihar districts, each maximizing a different hazard, so our demo shows real differentiation instead of similar results everywhere. Important: every district gets all 3 data types (flood, heat, crop-stress) — the district-per-hazard split below is just about which real-world event window we anchored each district's dates to, not which data type each district receives.
- **Flood-anchored — Katihar**: 2026-06-25 to 2026-07-10 (Ganga-Koshi flooding)
- **Heatwave-anchored — Gaya**: 2026-05-10 to 2026-05-25 (peak 44.6C on May 18)
- **Crop-stress-anchored — Begusarai**: 2026-07-01 to 2026-07-15 (46% rainfall deficit, kharif drought)

## **Data collected so far**

**Original batch (9 files, ~6.75 GB):** one Sentinel-1 (GRD), one Sentinel-2 (MSIL2A), and one Sentinel-3 (SL_1_RBT) product for each of the 3 districts, pulled from within each district's real event window.

**Begusarai additions (per teammate request):**
- 3 additional Sentinel-2 tiles (T45RVH, T45RUJ, T45RVJ) — the original tile only covered ~0.87% of Begusarai, so these neighboring tiles (same date, July 10, 2026) fill in full coverage
- 1 pre-flood Sentinel-1 image (July 2, 2026, VH+VV, same satellite/orbit-time as the July 14 flood image) — enables before/after change detection for flood extent mapping

**Sentinel-3 product correction:** the original SL_1_RBT product only contains raw brightness temperatures, not actual Land Surface Temperature. Re-pulled the correct SL_2_LST product for all 3 districts instead.

**Clipped/processed:**
- Sentinel-1 VH, georeferenced via GCPs and clipped to exact boundary: Katihar, Gaya, Begusarai (flood-day and pre-flood, pixel-aligned for change detection)
- Sentinel-2 bands (B02/B03/B04/B08), clipped to exact boundary: Katihar, Gaya, and Begusarai (4 tiles mosaicked into one seamless raster)
- Sentinel-3 LST, converted from scattered swath data to a gridded raster and clipped to exact boundary: Katihar, Gaya, Begusarai

Data lives in `data/<district>/` locally and is shared with the team via a Google Drive link (too large for GitHub; previously OneDrive, moved due to storage limits).

## **Scripts (in order of how they were built)**
- `filter_districts.py` — Filters GADM's all-India district file down to Katihar, Gaya, Begusarai, producing `target_districts.geojson`
- `find_one_product.py` — First working test, searches CDSE for one Sentinel-1 product over Katihar
- `search_katihar.py` — Searches Sentinel-1 products over Katihar (test point, then bounding box)
- `search_all_districts.py` — Extended search across all 3 districts and all 3 Sentinel missions
- `plan_downloads.py` — Dry-run, shows what would download and the total size before committing to it
- `get_katihar_ids.py` — Fetches Sentinel-2/3 product IDs for Katihar
- `get_gaya_begusarai_ids.py` — Fetches Sentinel-1/2/3 product IDs for Gaya and Begusarai
- `download_one.py` — Downloads Katihar's Sentinel-1 file, first successful real download
- `download_katihar_s2_s3.py` — Downloads Katihar's Sentinel-2 and Sentinel-3 files
- `download_gaya.py` — Downloads all 3 Sentinel files for Gaya
- `download_begusarai_retry.py` — Downloads all 3 Sentinel files for Begusarai, with retry and resume logic
- `find_begusarai_tiles.py` — Searches for all Sentinel-2 tiles intersecting Begusarai (found the coverage gap)
- `get_begusarai_missing_ids.py` — Fetches product IDs for the 3 neighboring gap-fill tiles
- `download_begusarai_missing_tiles.py` — Downloads the 3 gap-fill Sentinel-2 tiles
- `find_begusarai_preflood_s1.py` — Searches for a suitable pre-flood Sentinel-1 image
- `download_begusarai_preflood_s1.py` — Downloads the selected pre-flood Sentinel-1 product
- `clip_katihar_test.py` — First working GCP-georeference + exact-polygon-clip test for Sentinel-1 (proof of concept)
- `preview_katihar_clip.py` — Generates a quick visual PNG to sanity-check a clip looks like a real district shape
- `clip_all_sentinel1.py` — Scales the georeference + clip process across all Sentinel-1 VH rasters
- `check_s2_crs.py` — Confirms Sentinel-2 already has a proper CRS (no GCP workaround needed)
- `clip_katihar_sentinel2.py` — Clips Katihar's 4 key Sentinel-2 bands to exact boundary
- `clip_gaya_begusarai_sentinel2.py` — Clips Gaya's and all 4 Begusarai tiles' Sentinel-2 bands
- `mosaic_begusarai_sentinel2.py` — Merges Begusarai's 4 clipped Sentinel-2 tiles into one seamless raster per band
- `find_gaya_lst.py` — Searches for the correct SL_2_LST product (Gaya), after discovering SL_1_RBT wasn't the right product for LST
- `download_gaya_lst.py` — Downloads Gaya's SL_2_LST product
- `inspect_lst.py` — Inspects the internal structure of an LST NetCDF file
- `grid_gaya_lst.py` — Converts Gaya's scattered-swath LST data into a proper gridded GeoTIFF
- `clip_gaya_lst.py` — Clips Gaya's gridded LST to the exact district boundary, with a visual preview
- `find_katihar_begusarai_lst.py` — Searches for SL_2_LST products for Katihar and Begusarai
- `download_katihar_begusarai_lst.py` — Downloads both
- `grid_clip_katihar_begusarai_lst.py` — Grids and clips both to their exact district boundaries

## **What's NOT done yet**
- VV polarization hasn't been clipped yet for Sentinel-1, only VH
- Radiometric correction, calibration, and cloud masking still to come (next stage, likely Supriya's)
- No automated scheduling yet — everything so far has been run manually, one script at a time
- LST passes were captured at different times of day per district (e.g. Gaya's pass was evening, not peak daytime heat) — worth flagging to Supriya/Ayush so LST values aren't misread as "not that hot"

## **What I'm doing next**
1. Confirm with Supriya that the current LST product and pass-times work for her needs, or whether we should pull daytime passes specifically
2. Turn the manual scripts into an actual scheduled/automated pipeline
3. Possibly pull VV clips too, since flood detection sometimes benefits from both polarizations

## **Accessing the data**
The actual satellite imagery (multiple GB, raw + clipped) is NOT in this repo — GitHub can't host files this large. It's shared via Google Drive instead: https://drive.google.com/drive/folders/1M1NjGPJ3Yeau8If4ffGxIJB09NXadSj7?usp=drive_link

These are already-extracted Sentinel `.SAFE`/`.SEN3` products — no need to unzip anything, just open the relevant folder and start working with the raw files inside. Files ending in `_clipped.tiff` are the processed, analysis-ready versions, already cropped to the exact district boundary (not just a bounding box). Sentinel-3 LST files also have a `_gridded.tiff` intermediate version, in case the raw scattered-point data is needed instead of the clipped grid.
