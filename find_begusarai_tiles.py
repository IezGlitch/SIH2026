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
token = r.json()["access_token"]

gdf = gpd.read_file("target_districts.geojson")
row = gdf[gdf["NAME_2"] == "Begusarai"]
geom_wkt = row.geometry.iloc[0].envelope.wkt
print("Begusarai bounding box:", geom_wkt)

filt = (
    f"Collection/Name eq 'SENTINEL-2' and contains(Name,'MSIL2A') and "
    f"OData.CSC.Intersects(area=geography'SRID=4326;{geom_wkt}') and "
    f"ContentDate/Start gt 2026-07-05T00:00:00.000Z and ContentDate/Start lt 2026-07-15T00:00:00.000Z"
)
resp = requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products",
                     params={"$filter": filt, "$top": 20, "$orderby": "ContentDate/Start desc"},
                     headers={"Authorization": f"Bearer {token}"})
results = resp.json()

if "value" in results:
    print(f"\nFound {len(results['value'])} products:\n")
    for p in results["value"]:
        print("-", p["Name"])
else:
    print(results)