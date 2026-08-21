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
    {"id": "30c1e837-3e1a-46c7-9387-c1e35413e3d4", "output": "data/Katihar/katihar_sentinel3_lst_20260709.zip"},
    {"id": "a81297cd-b51a-4f8a-a980-f7a780f72684", "output": "data/Begusarai/begusarai_sentinel3_lst_20260713.zip"},
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