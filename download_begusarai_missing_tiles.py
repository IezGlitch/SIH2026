from dotenv import load_dotenv
import os
import requests
import time

load_dotenv()
CDSE_USERNAME = os.getenv("CDSE_USERNAME")
CDSE_PASSWORD = os.getenv("CDSE_PASSWORD")

os.makedirs("data/begusarai", exist_ok=True)

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
    {"id": "3a9a929c-37d9-493e-96b3-d5e325c74104", "output": "data/begusarai/begusarai_sentinel2_T45RVH.zip"},
    {"id": "5ac52cbc-f474-4a58-979b-1adc12bc0a24", "output": "data/begusarai/begusarai_sentinel2_T45RUJ.zip"},
    {"id": "65385e65-337d-4ae3-9fc1-cdd8ba6d7613", "output": "data/begusarai/begusarai_sentinel2_T45RVJ.zip"},
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