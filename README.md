# **Data Ingestion Pipeline — Mitali** 



This covers my part of SOAIDEATHON-S6: fetching raw Sentinel-1, Sentinel-2, and Sentinel-3 satellite imagery from the Copernicus Data Space Ecosystem (CDSE) for our 3 target districts.



## **What I built**



An end-to-end pipeline that:

1\. Takes India's official district boundaries (GADM) and filters them down to our 3 target districts

2\. Authenticates with CDSE (OAuth)

3\. Searches CDSE's catalogue for Sentinel-1/2/3 products covering each district during a specific real-world event window

4\. Downloads the actual satellite files, with retry/resume logic for unstable connections

5\. Organizes everything into a clean folder structure for the rest of the team



## **Target districts**



I picked 3 Bihar districts, each maximizing a different hazard, so our demo shows real differentiation instead of similar results everywhere:



\- **Flood — Katihar**: 2026-06-25 to 2026-07-10 (Ganga-Koshi flooding)

\- **Heatwave — Gaya**: 2026-05-10 to 2026-05-25 (peak 44.6C on May 18)

\- **Crop stress — Begusarai**: 2026-07-01 to 2026-07-15 (46% rainfall deficit, kharif drought)



## **Data collected so far**



9 files total, \~6.75 GB — one Sentinel-1 (GRD), one Sentinel-2 (MSIL2A), and one Sentinel-3 (SL\_1\_RBT) product for each of the 3 districts above, all pulled from within that district's real event window.



Data lives in `data/<district>/` locally and is shared with the team via a OneDrive link (too large for GitHub).



## **Scripts (in order of how they were built)**



\- `filter_districts.py` — Filters GADM's all-India district file down to Katihar, Gaya, Begusarai, producing `target_districts.geojson`

\- `find_one_product.py` — First working test, searches CDSE for one Sentinel-1 product over Katihar

\- `search_katihar.py` — Searches Sentinel-1 products over Katihar (test point, then bounding box)

\- `search_all_districts.py` — Extended search across all 3 districts and all 3 Sentinel missions

\- `plan_downloads.py` — Dry-run, shows what would download and the total size before committing to it

\- `get_katihar_ids.py` — Fetches Sentinel-2/3 product IDs for Katihar

\- `get_gaya_begusarai_ids.py` — Fetches Sentinel-1/2/3 product IDs for Gaya and Begusarai

\- `download_one.py` — Downloads Katihar's Sentinel-1 file, first successful real download

\- `download_katihar_s2_s3.py` — Downloads Katihar's Sentinel-2 and Sentinel-3 files

\- `download_gaya.py` — Downloads all 3 Sentinel files for Gaya

\- `download_begusarai_retry.py` — Downloads all 3 Sentinel files for Begusarai, with retry and resume logic since the connection kept dropping on large files



## **What's NOT done yet**



\- Only one snapshot per district/satellite — no before/after imagery yet for comparing change over time

\- Using bounding boxes, not each district's exact shape — some extra area outside the district is included

\- Data is raw/unprocessed — no correction, calibration, or cloud masking applied yet, that's the next stage

\- No automated scheduling yet — everything so far has been run manually, one script at a time



## **What I'm doing next**



1\. Clip the downloaded imagery to each district's exact boundary instead of its bounding box

2\. Pull an earlier "before" snapshot per district so there's something to compare against

3\. Turn the manual scripts into an actual scheduled/automated pipeline

4\. Confirm with Supriya that the Sentinel-3 product type I picked works for her LST calculations

## **Accessing the data**

The actual satellite imagery (~6.75 GB, 9 folders) is NOT in this repo — GitHub can't host files this large. It's shared via OneDrive instead: https://1drv.ms/f/c/a0976f237df6e1f7/IgBV0f4ezwv2RaFitZbJaFQ7AUCimqKt1HwKjNP0oFTyGqg?e=GSvSfk

These are already-extracted Sentinel `.SAFE` products — no need to unzip anything, just open the relevant folder and start working with the raw files inside.
