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

districts = {
    "Katihar":   ("2026-06-25T00:00:00.000Z", "2026-07-10T00:00:00.000Z"),
    "Begusarai": ("2026-07-01T00:00:00.000Z", "2026-07-15T00:00:00.000Z"),
}

for district, (start, end) in districts.items():
    row = gdf[gdf["NAME_2"] == district]
    geom_wkt = row.geometry.iloc[0].envelope.wkt

    filt = (
        f"Collection/Name eq 'SENTINEL-3' and contains(Name,'SL_2_LST') and "
        f"OData.CSC.Intersects(area=geography'SRID=4326;{geom_wkt}') and "
        f"ContentDate/Start gt {start} and ContentDate/Start lt {end}"
    )
    resp = requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products",
                         params={"$filter": filt, "$top": 5, "$orderby": "ContentDate/Start desc"},
                         headers={"Authorization": f"Bearer {token}"})
    results = resp.json()

    print(f"\n--- {district} ---")
    if "value" in results and len(results["value"]) > 0:
        for p in results["value"]:
            print("-", p["Name"], "| Id:", p["Id"])
    else:
        print("NOT FOUND:", results)