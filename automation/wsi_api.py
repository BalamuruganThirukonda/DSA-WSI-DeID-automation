# automation/wsi_api.py
import requests
import json
from config import GIRDER_URL, API_KEY

# =========================
# Girder Token Handling
# =========================
def get_girder_token():
    """
    Get a temporary Girder token using the API key.
    Tokens are valid for a limited time, so this is called before every API action.
    """
    url = f"{GIRDER_URL}/api_key/token?key={API_KEY}"
    response = requests.post(url, headers={"Content-Length": "0"})
    response.raise_for_status()
    token = response.json()["authToken"]["token"]
    return token

# =========================
# WSI DeID Actions
# =========================
def ingest():
    """
    Ingest files from the import folder into WSI DeID.
    """
    token = get_girder_token()
    url = f"{GIRDER_URL}/wsi_deid/action/ingest"
    response = requests.put(url, headers={"Girder-Token": token, "Content-Length": "0"})
    response.raise_for_status()
    return response.json()


def process_items(item_ids):
    """
    Redact a batch of items by their item IDs.
    :param item_ids: list of item _id strings
    """
    token = get_girder_token()
    url = f"{GIRDER_URL}/wsi_deid/action/list/process"
    data = {"ids": json.dumps(item_ids)}
    response = requests.put(url, headers={"Girder-Token": token}, data=data)
    response.raise_for_status()
    return response.json()


def approve_items(item_ids):
    """
    Approve a batch of items by their item IDs.
    :param item_ids: list of item _id strings
    """
    token = get_girder_token()
    url = f"{GIRDER_URL}/wsi_deid/action/list/finish"
    data = {"ids": json.dumps(item_ids)}
    response = requests.put(url, headers={"Girder-Token": token}, data=data)
    response.raise_for_status()
    return response.json()


def export():
    """
    Export all recently approved and redacted items.
    """
    token = get_girder_token()
    url = f"{GIRDER_URL}/wsi_deid/action/export"
    response = requests.put(url, headers={"Girder-Token": token, "Content-Length": "0"})
    response.raise_for_status()
    return response.json()


def get_status():
    """
    Get current processing status of all items in WSI DeID.
    """
    token = get_girder_token()
    url = f"{GIRDER_URL}/wsi_deid/status"
    response = requests.get(url, headers={"Girder-Token": token})
    response.raise_for_status()
    return response.json()