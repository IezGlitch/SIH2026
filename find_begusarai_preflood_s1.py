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

filt = (
    f"Collection/Name eq 'SENTINEL-1' and contains(Name,'GRD') and contains(Name,'IW') and "
    f"OData.CSC.Intersects(area=geography'SRID=4326;{geom_wkt}') and "
    f"ContentDate/Start gt 2026-06-25T00:00:00.000Z and ContentDate/Start lt 2026-07-13T00:00:00.000Z"
)
resp = requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products",
                     params={"$filter": filt, "$top": 20, "$orderby": "ContentDate/Start desc"},
                     headers={"Authorization": f"Bearer {token}"})
results = resp.json()

if "value" in results:
    print(f"Found {len(results['value'])} products:\n")
    for p in results["value"]:
        print("-", p["Name"], "| Id:", p["Id"])
else:
    print(results)