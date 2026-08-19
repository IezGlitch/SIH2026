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
    {
        "id": "11abfdbb-c7ac-483c-8e14-f69b827e8f0b",
        "name": "S2C_MSIL2A_20260707T043701_N0512_R033_T45RWJ_20260707T090407.SAFE",
        "output": "katihar_sentinel2_sample.zip"
    },
    {
        "id": "bb918dcf-156e-47b7-b396-a00c1091c554",
        "name": "S3A_SL_1_RBT____20260709T155342...SEN3",
        "output": "katihar_sentinel3_sample.zip"
    }
]

token = get_token()
print("Got access token successfully.")

for product in products:
    download_url = f"https://zipper.dataspace.copernicus.eu/odata/v1/Products({product['id']})/$value"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"\nDownloading {product['name']}...")
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