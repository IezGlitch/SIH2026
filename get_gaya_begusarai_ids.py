from dotenv import load_dotenv
import os
import geopandas as gpd
import requests

load_dotenv()
CDSE_USERNAME = os.getenv("CDSE_USERNAME")
CDSE_PASSWORD = os.getenv("CDSE_PASSWORD")

token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
r = requests.post(token_url, data={
    "grant_type": "password", "username": CDSE_USERNAME,
    "password": CDSE_PASSWORD, "client_id": "cdse-public"
})
print("Status code:", r.status_code)
token = r.json()["access_token"]

gdf = gpd.read_file("target_districts.geojson")

districts = {
    "Gaya":      ("2026-05-10T00:00:00.000Z", "2026-05-25T00:00:00.000Z"),
    "Begusarai": ("2026-07-01T00:00:00.000Z", "2026-07-15T00:00:00.000Z"),
}

collections = {
    "SENTINEL-1": "contains(Name,'GRD')",
    "SENTINEL-2": "contains(Name,'MSIL2A')",
    "SENTINEL-3": "contains(Name,'SL_1_RBT')",
}

for district, (start, end) in districts.items():
    row = gdf[gdf["NAME_2"] == district]
    geom_wkt = row.geometry.iloc[0].envelope.wkt

    for collection, extra in collections.items():
        filt = (
            f"Collection/Name eq '{collection}' and {extra} and "
            f"OData.CSC.Intersects(area=geography'SRID=4326;{geom_wkt}') and "
            f"ContentDate/Start gt {start} and ContentDate/Start lt {end}"
        )
        resp = requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products",
                             params={"$filter": filt, "$top": 1, "$orderby": "ContentDate/Start desc"},
                             headers={"Authorization": f"Bearer {token}"})
        results = resp.json()
        if "value" in results and len(results["value"]) > 0:
            p = results["value"][0]
            print(f"{district} / {collection} -> {p['Id']} | {p['Name']}")
        else:
            print(f"{district} / {collection} -> NOT FOUND")