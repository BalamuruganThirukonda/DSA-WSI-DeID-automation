import requests
import os

# =========================
# CONFIG
# =========================
API_KEY = "DY4LmGEkkYKiHjpRXnEMfo3YY4NRf5tcIgD2bSe8"
BASE_URL = "http://localhost:8080/api/v1"

IMPORT_CONTAINER_PATH = "/import"   # inside docker container


def get_token():
    r = requests.post(
        f"{BASE_URL}/api_key/token",
        params={"key": API_KEY}
    )
    r.raise_for_status()
    return r.json()["authToken"]["token"]


def check_import_folder():
    print("Checking import folder inside container...")
    os.system("docker exec -it wsi_deid-girder-1 ls /import")


def trigger_ingest(token):
    print("Triggering ingest...")
    r = requests.put(
        f"{BASE_URL}/wsi_deid/action/ingest",
        headers={
            "Girder-Token": token,
            "Content-Length": "0"
        }
    )
    r.raise_for_status()
    print("Ingest response:")
    print(r.json())


if __name__ == "__main__":
    token = get_token()
    print("Token acquired.")

    check_import_folder()
    trigger_ingest(token)