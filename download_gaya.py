from dotenv import load_dotenv
import os
import requests

load_dotenv()
CDSE_USERNAME = os.getenv("CDSE_USERNAME")
CDSE_PASSWORD = os.getenv("CDSE_PASSWORD")

def get_token():
    token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    r = requests.post(token_url, data={
        "grant_type": "password",
        "username": CDSE_USERNAME,
        "password": CDSE_PASSWORD,
        "client_id": "cdse-public"
    })
    return r.json()["access_token"]

products = [
    {"id": "30436122-737d-46ce-9598-53f9c144cdba", "output": "gaya_sentinel1_sample.zip"},
    {"id": "039e5da1-c4af-4594-bffa-87def3da3a6d", "output": "gaya_sentinel2_sample.zip"},
    {"id": "3c65a86b-0aa0-4b48-a36a-cf8f41dac2ae", "output": "gaya_sentinel3_sample.zip"},
]

token = get_token()
print("Got access token successfully.")

for product in products:
    download_url = f"https://zipper.dataspace.copernicus.eu/odata/v1/Products({product['id']})/$value"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"\nDownloading {product['output']}...")
    response = requests.get(download_url, headers=headers, stream=True)
    print("Status code:", response.status_code)

    if response.status_code == 200:
        total_size = 0
        with open(product["output"], "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    total_size += len(chunk)
                    print(f"\rDownloaded: {total_size / (1024*1024):.1f} MB", end="")
        print(f"\nDone. Saved as {product['output']}")
    else:
        print("Download failed:", response.text[:500])