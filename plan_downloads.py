from dotenv import load_dotenv
import os
import geopandas as gpd
import requests

load_dotenv()
CDSE_USERNAME = os.getenv("CDSE_USERNAME")
CDSE_PASSWORD = os.getenv("CDSE_PASSWORD")

gdf = gpd.read_file("target_districts.geojson")

districts = {
    "Katihar":   ("2026-06-25T00:00:00.000Z", "2026-07-10T00:00:00.000Z"),
    "Gaya":      ("2026-05-10T00:00:00.000Z", "2026-05-25T00:00:00.000Z"),
    "Begusarai": ("2026-07-01T00:00:00.000Z", "2026-07-15T00:00:00.000Z"),
}

collections = {
    "SENTINEL-1": "contains(Name,'GRD')",
    "SENTINEL-2": "contains(Name,'MSIL2A')",
    "SENTINEL-3": "contains(Name,'SL_1_RBT')",
}

def get_token():
    token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    r = requests.post(token_url, data={
        "grant_type": "password",
        "username": CDSE_USERNAME,
        "password": CDSE_PASSWORD,
        "client_id": "cdse-public"
    })
    return r.json()["access_token"]

search_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
token = get_token()

os.makedirs("data", exist_ok=True)
plan = []

for district, (start, end) in districts.items():
    row = gdf[gdf["NAME_2"] == district]
    bbox = row.geometry.iloc[0].envelope
    geom_wkt = bbox.wkt

    for collection, extra_filter in collections.items():
        filter_str = (
            f"Collection/Name eq '{collection}' and "
            f"{extra_filter} and "
            f"OData.CSC.Intersects(area=geography'SRID=4326;{geom_wkt}') and "
            f"ContentDate/Start gt {start} and ContentDate/Start lt {end}"
        )
        params = {"$filter": filter_str, "$top": 1, "$orderby": "ContentDate/Start desc"}
        headers = {"Authorization": f"Bearer {token}"}

        r = requests.get(search_url, params=params, headers=headers)
        results = r.json()

        if "value" in results and len(results["value"]) > 0:
            p = results["value"][0]
            size_mb = int(p.get("ContentLength", 0)) / (1024*1024)
            plan.append({
                "district": district,
                "collection": collection,
                "name": p["Name"],
                "id": p["Id"],
                "size_mb": size_mb
            })
            print(f"{district} / {collection}: {p['Name']} ({size_mb:.1f} MB)")
        else:
            print(f"{district} / {collection}: NO PRODUCT FOUND")

total_gb = sum(item["size_mb"] for item in plan) / 1024
print(f"\nTOTAL PLANNED DOWNLOAD SIZE: {total_gb:.2f} GB across {len(plan)} files")