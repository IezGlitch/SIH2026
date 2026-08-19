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
katihar = gdf[gdf["NAME_2"] == "Katihar"]
bbox = katihar.geometry.iloc[0].envelope
geom_wkt = bbox.wkt
print("Katihar bounding box:", geom_wkt)

search_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
params = {
    "$filter": f"Collection/Name eq 'SENTINEL-1' and OData.CSC.Intersects(area=geography'SRID=4326;{geom_wkt}')",
    "$top": 5
}
headers = {"Authorization": f"Bearer {access_token}"}

response = requests.get(search_url, params=params, headers=headers)
print("Status code:", response.status_code)

results = response.json()
if "value" in results:
    print(f"\nFound {len(results['value'])} products:")
    for p in results["value"]:
        print("-", p["Name"])
else:
    print(results)