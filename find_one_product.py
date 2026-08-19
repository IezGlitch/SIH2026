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
row = gdf[gdf["NAME_2"] == "Katihar"]
bbox = row.geometry.iloc[0].envelope
geom_wkt = bbox.wkt

search_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
filter_str = (
    f"Collection/Name eq 'SENTINEL-1' and "
    f"contains(Name,'GRD') and "
    f"OData.CSC.Intersects(area=geography'SRID=4326;{geom_wkt}') and "
    f"ContentDate/Start gt 2026-06-25T00:00:00.000Z and ContentDate/Start lt 2026-07-10T00:00:00.000Z"
)
params = {"$filter": filter_str, "$top": 1, "$orderby": "ContentDate/Start desc"}
headers = {"Authorization": f"Bearer {access_token}"}

response = requests.get(search_url, params=params, headers=headers)
results = response.json()

print("Status code:", response.status_code)
if "value" in results and len(results["value"]) > 0:
    product = results["value"][0]
    print("Product Name:", product["Name"])
    print("Product ID:", product["Id"])
    print("Size (bytes):", product.get("ContentLength", "unknown"))
else:
    print("No product found:", results)