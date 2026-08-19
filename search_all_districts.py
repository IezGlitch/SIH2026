from dotenv import load_dotenv
import os
import geopandas as gpd
import requests

load_dotenv()
CLIENT_ID = os.getenv("CDSE_CLIENT_ID")
CLIENT_SECRET = os.getenv("CDSE_CLIENT_SECRET")

token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
token_response = requests.post(token_url, data={
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
})
access_token = token_response.json()["access_token"]
print("Got access token successfully.")

gdf = gpd.read_file("target_districts.geojson")

districts = {
    "Katihar":   ("2026-06-25T00:00:00.000Z", "2026-07-10T00:00:00.000Z"),
    "Gaya":      ("2026-05-10T00:00:00.000Z", "2026-05-25T00:00:00.000Z"),
    "Begusarai": ("2026-07-01T00:00:00.000Z", "2026-07-15T00:00:00.000Z"),
}

collections = ["SENTINEL-1", "SENTINEL-2", "SENTINEL-3"]

search_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
headers = {"Authorization": f"Bearer {access_token}"}

for district, (start, end) in districts.items():
    row = gdf[gdf["NAME_2"] == district]
    bbox = row.geometry.iloc[0].envelope
    geom_wkt = bbox.wkt

    print(f"\n########## {district} ({start[:10]} to {end[:10]}) ##########")

    for collection in collections:
        filter_str = (
            f"Collection/Name eq '{collection}' and "
            f"OData.CSC.Intersects(area=geography'SRID=4326;{geom_wkt}') and "
            f"ContentDate/Start gt {start} and ContentDate/Start lt {end}"
        )
        params = {"$filter": filter_str, "$top": 5}

        response = requests.get(search_url, params=params, headers=headers)
        results = response.json()

        print(f"\n--- {collection} ---")
        print("Status code:", response.status_code)
        if "value" in results:
            print(f"Found {len(results['value'])} products:")
            for p in results["value"]:
                print("-", p["Name"])
        else:
            print(results)