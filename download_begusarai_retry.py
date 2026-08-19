from dotenv import load_dotenv
import os
import requests
import time

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
    {"id": "b38f34a6-5373-49a9-86b0-95ea3d345a8c", "output": "begusarai_sentinel1_sample.zip"},
    {"id": "39c26947-49d0-4a25-8f86-04f24eadb6ac", "output": "begusarai_sentinel2_sample.zip"},
    {"id": "fc039df2-a0c6-4e3b-bc28-df5b52b23f95", "output": "begusarai_sentinel3_sample.zip"},
]

def download_resumable(product, max_retries=8):
    url = f"https://zipper.dataspace.copernicus.eu/odata/v1/Products({product['id']})/$value"
    out_path = product["output"]

    for attempt in range(1, max_retries + 1):
        existing_size = os.path.getsize(out_path) if os.path.exists(out_path) else 0
        token = get_token()
        headers = {"Authorization": f"Bearer {token}"}
        if existing_size > 0:
            headers["Range"] = f"bytes={existing_size}-"
            print(f"\nResuming {out_path} from {existing_size / (1024*1024):.1f} MB (attempt {attempt})...")
        else:
            print(f"\nStarting {out_path} (attempt {attempt})...")

        try:
            response = requests.get(url, headers=headers, stream=True, timeout=120)
            print("Status code:", response.status_code)

            if response.status_code in (200, 206):
                mode = "ab" if response.status_code == 206 else "wb"
                total = existing_size if mode == "ab" else 0
                with open(out_path, mode) as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            total += len(chunk)
                            print(f"\rDownloaded: {total / (1024*1024):.1f} MB", end="")
                print(f"\nFinished attempt for {out_path}")
                return True
            else:
                print("Unexpected status:", response.text[:300])
        except Exception as e:
            print(f"\nAttempt {attempt} failed: {e}")

        print("Retrying in 5 seconds...")
        time.sleep(5)

    print(f"Gave up on {out_path} after {max_retries} attempts.")
    return False

for product in products:
    download_resumable(product)