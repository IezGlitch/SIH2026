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
row = gdf[gdf["NAME_2"] == "Katihar"]
geom_wkt = row.geometry.iloc[0].envelope.wkt

for collection, extra in [("SENTINEL-2", "contains(Name,'MSIL2A')"), ("SENTINEL-3", "contains(Name,'SL_1_RBT')")]:
    filt = f"Collection/Name eq '{collection}' and {extra} and OData.CSC.Intersects(area=geography'SRID=4326;{geom_wkt}') and ContentDate/Start gt 2026-06-25T00:00:00.000Z and ContentDate/Start lt 2026-07-10T00:00:00.000Z"
    resp = requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products",
                         params={"$filter": filt, "$top": 1, "$orderby": "ContentDate/Start desc"},
                         headers={"Authorization": f"Bearer {token}"})
    p = resp.json()["value"][0]
    print(collection, "->", p["Id"], "|", p["Name"])