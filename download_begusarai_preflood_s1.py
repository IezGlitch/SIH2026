from dotenv import load_dotenv
import os
import requests

load_dotenv()
CDSE_USERNAME = os.getenv("CDSE_USERNAME")
CDSE_PASSWORD = os.getenv("CDSE_PASSWORD")

os.makedirs("data/begusarai", exist_ok=True)

PRODUCT_ID = "8a7d1e45-df37-4f20-9389-85503da6c676"
OUTPUT_FILE = "data/begusarai/begusarai_sentinel1_preflood_20260702.zip"

token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
token_response = requests.post(token_url, data={
    "grant_type": "password",
    "username": CDSE_USERNAME,
    "password": CDSE_PASSWORD,
    "client_id": "cdse-public"
})
access_token = token_response.json()["access_token"]
print("Got access token successfully.")

download_url = f"https://zipper.dataspace.copernicus.eu/odata/v1/Products({PRODUCT_ID})/$value"
headers = {"Authorization": f"Bearer {access_token}"}

print("Starting download...")
response = requests.get(download_url, headers=headers, stream=True)
print("Status code:", response.status_code)

if response.status_code == 200:
    total_size = 0
    with open(OUTPUT_FILE, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                total_size += len(chunk)
                print(f"\rDownloaded: {total_size / (1024*1024):.1f} MB", end="")
    print(f"\nDone. Saved as {OUTPUT_FILE}")
else:
    print("Download failed:", response.text[:500])