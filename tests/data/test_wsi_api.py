# automation/test_wsi_api.py

import os
import time
import pandas as pd

from manifest_generator import generate_manifest
from wsi_api import ingest, process_items, approve_items, export, get_status
from config import LOCAL_IMPORT_PATH, MANIFEST_FILENAME


def get_item_ids_from_status(expected_names):
    """
    Fetch Girder item IDs from AvailableToProcess folder
    using DeID filenames.
    """
    status = get_status()

    # Find AvailableToProcess folder
    available_folder = None
    for fid, folder in status.get("folders", {}).items():
        if folder.get("key") == "histomicsui.ingest_folder":
            available_folder = folder
            break

    if not available_folder:
        raise Exception("AvailableToProcess folder not found")

    items = available_folder.get("items", {})

    print("\n[DEBUG] Items currently in AvailableToProcess:")
    for item_id, info in items.items():
        print("   ", info.get("name"))

    result_ids = []

    for item_id, item_info in items.items():
        if item_info.get("name") in expected_names:
            result_ids.append(item_id)

    return result_ids


def run_test_pipeline():
    print("=== Starting Full Pipeline Test ===\n")

    # Step 1: Generate manifest
    if not generate_manifest():
        print("[!] No SVS files found in import folder. Exiting.")
        return

    print("[+] Manifest generated successfully")

    manifest_path = os.path.join(LOCAL_IMPORT_PATH, MANIFEST_FILENAME)
    df = pd.read_excel(manifest_path)

    # 🔥 IMPORTANT FIX: Use SampleID to build DeID filenames
    expected_names = [f"{sid}.svs" for sid in df["SampleID"].tolist()]

    print("\nExpected DeID filenames:")
    for name in expected_names:
        print("   ", name)

    # Step 2: Ingest
    try:
        ingest_result = ingest()
        print("\n[+] Ingest result:", ingest_result)
    except Exception as e:
        print("[!] Ingest failed:", e)
        return

    # Wait a few seconds to ensure Girder registers items
    print("\nWaiting for items to appear in AvailableToProcess...")
    time.sleep(3)

    # Step 3: Fetch item IDs
    try:
        item_ids = get_item_ids_from_status(expected_names)

        if not item_ids:
            print("\n[!] No matching items found after ingest.")
            print("Check filename mapping between manifest and WSI-DeID.")
            return

        print(f"\n[+] Found {len(item_ids)} item IDs for processing")
    except Exception as e:
        print("[!] Failed to fetch item IDs:", e)
        return

    # Step 4: Process (Redact)
    try:
        process_result = process_items(item_ids)
        print("\n[+] Redact result:", process_result)
    except Exception as e:
        print("[!] Redact failed:", e)
        return

    # Step 5: Approve
    try:
        approve_result = approve_items(item_ids)
        print("\n[+] Approve result:", approve_result)
    except Exception as e:
        print("[!] Approve failed:", e)
        return

    # Step 6: Export
    try:
        export_result = export()
        print("\n[+] Export result:", export_result)
    except Exception as e:
        print("[!] Export failed:", e)
        return

    print("\n[✔] Full pipeline test completed successfully!")


if __name__ == "__main__":
    run_test_pipeline()