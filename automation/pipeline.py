import os
import time
import shutil
import pandas as pd
from datetime import datetime

from automation.manifest_generator import generate_manifest
from automation.wsi_api import ingest, process_items, approve_items, export, get_status, delete_items
from automation.config import (
    IMPORT_FOLDER,
    LOCAL_IMPORT_PATH,
    LOCAL_EXPORT_PATH,
    ARCHIVE_FOLDER,
    MANIFEST_FILENAME,
    BATCH_SIZE,
    PROCESSED_FILE_ACTION,
    DELETE_EXPORT_JOB_FILES
)
from automation.db_logger import initialize_database, insert_processed_files, export_history_to_excel

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

# ---------------------------------------------------
# Wait until file stops growing (copy finished)
# ---------------------------------------------------
def wait_for_file_stable(path, wait_seconds=2):
    try:
        size1 = os.path.getsize(path)
        time.sleep(wait_seconds)
        size2 = os.path.getsize(path)
        return size1 == size2
    except:
        return False

# ---------------------------------------------------
# Move batch of slides from Import → Process folder
# Handles subfolders and only moves stable files
# ---------------------------------------------------
def move_batch_from_import():
    all_files = []

    for root, _, files in os.walk(IMPORT_FOLDER):
        for f in files:
            if f.lower().endswith(".svs"):
                all_files.append(os.path.join(root, f))

    if not all_files:
        return []

    batch = all_files[:BATCH_SIZE]
    moved_files = []

    for src in batch:
        if not wait_for_file_stable(src):
            log(f"Skipping (still copying): {src}")
            continue

        filename = os.path.basename(src)
        os.makedirs(LOCAL_IMPORT_PATH, exist_ok=True)
        dst = os.path.join(LOCAL_IMPORT_PATH, filename)

        try:
            shutil.move(src, dst)
            moved_files.append(filename)
            log(f"Moved → process: {filename}")
        except Exception as e:
            log(f"Move failed: {filename} ({e})")

    cleanup_empty_import_folders()

    return moved_files

def cleanup_empty_import_folders():
    """
    Remove empty folders inside IMPORT_FOLDER.
    Walks bottom-up so nested folders are handled correctly.
    """
    for root, dirs, files in os.walk(IMPORT_FOLDER, topdown=False):

        # Skip the main import folder itself
        if root == IMPORT_FOLDER:
            continue

        if not os.listdir(root):
            try:
                os.rmdir(root)
                log(f"Removed empty import folder: {root}")
            except Exception as e:
                log(f"Could not remove folder {root}: {e}")

# ---------------------------------------------------
# Get item IDs from Girder
# ---------------------------------------------------
def get_item_ids_from_status(expected_names):
    status = get_status()

    available_folder = None
    for fid, folder in status.get("folders", {}).items():
        if folder.get("key") == "histomicsui.ingest_folder":
            available_folder = folder
            break

    if not available_folder:
        raise Exception("AvailableToProcess folder not found")

    items = available_folder.get("items", {})

    log("Items currently in AvailableToProcess:")
    for item_id, info in items.items():
        log(f"   {info.get('name')}")

    result_ids = [
        item_id for item_id, info in items.items()
        if info.get("name") in expected_names
    ]

    return result_ids

# ---------------------------------------------------
# Remove DeID Export Job Excel files
# ---------------------------------------------------
def cleanup_export_job_files():

    if not DELETE_EXPORT_JOB_FILES:
        return

    export_folder = LOCAL_EXPORT_PATH  # or your EXPORT folder if different

    removed = 0

    for f in os.listdir(export_folder):

        if f.startswith("DeID Export Job") and f.endswith(".xlsx"):
            try:
                os.remove(os.path.join(export_folder, f))
                removed += 1
            except Exception as e:
                log(f"Failed to delete export job file {f}: {e}")

    if removed > 0:
        log(f"Removed {removed} DeID Export Job files")


# ---------------------------------------------------
# Main pipeline function (processes a batch)
# ---------------------------------------------------
def run_test_pipeline():
    log("=== Starting Pipeline Cycle ===")

    # ------------------------------
    # Step 1: Move batch from Import → Process
    # ------------------------------
    batch_files = move_batch_from_import()
    if not batch_files:
        log("No slides found in Import folder.")
        return False

    log(f"Batch ready ({len(batch_files)} slides)")

    # ------------------------------
    # Step 2: Generate Manifest
    # ------------------------------
    manifest_path = os.path.join(LOCAL_IMPORT_PATH, MANIFEST_FILENAME)
    if not generate_manifest(batch_files, manifest_path):
        log("Manifest generation failed.")
        return False

    log(f"Manifest generated: {manifest_path}")

    df = pd.read_excel(manifest_path)
    expected_names = [f"{sid}.svs" for sid in df["SampleID"].tolist()]

    log("Expected DeID filenames:")
    for name in expected_names:
        log(f"   {name}")

    # ------------------------------
    # Step 3: Ingest
    # ------------------------------
    try:
        ingest_result = ingest()
        log(f"Ingest result: {ingest_result}")
    except Exception as e:
        log(f"Ingest failed: {e}")
        return False

    # ------------------------------
    # Step 4: Wait for items to appear
    # ------------------------------
    retries = 10
    item_ids = []

    for _ in range(retries):
        time.sleep(3)
        item_ids = get_item_ids_from_status(expected_names)
        if item_ids:
            break

    if not item_ids:
        log("No matching items found after ingest.")
        return False

    log(f"Found {len(item_ids)} item IDs")

    # ------------------------------
    # Step 5: Redact
    # ------------------------------
    try:
        result = process_items(item_ids)
        log(f"Redact result: {result}")
    except Exception as e:
        log(f"Redact failed: {e}")
        return False

    # ------------------------------
    # Step 6: Approve
    # ------------------------------
    try:
        result = approve_items(item_ids)
        log(f"Approve result: {result}")
    except Exception as e:
        log(f"Approve failed: {e}")
        return False

    # ------------------------------
    # Step 7: Export
    # ------------------------------
    try:
        result = export()
        log(f"Export result: {result}")
    except Exception as e:
        log(f"Export failed: {e}")
        return False

    # ------------------------------------------------
    # Step 7.1: Remove DeID Export Job excel files
    # ------------------------------------------------
    cleanup_export_job_files()

    # ------------------------------
    # Step 8: Delete items from Girder
    # ------------------------------
    try:
        deleted = delete_items(item_ids)
        log(f"Deleted {deleted} items from Girder")
    except Exception as e:
        log(f"Delete failed: {e}")
        return False

    # ------------------------------
    # Step 9: Log to database
    # ------------------------------
    try:
        initialize_database()
        insert_processed_files(df)
        excel_path = export_history_to_excel()
        log(f"Excel history updated: {excel_path}")
    except Exception as e:
        log(f"Database logging failed: {e}")
        return False

    # ------------------------------
    # Step 10: Archive processed slides
    # ------------------------------
    if PROCESSED_FILE_ACTION == "move":

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_folder = os.path.join(ARCHIVE_FOLDER, f"batch_{timestamp}")
        os.makedirs(batch_folder, exist_ok=True)

        for f in batch_files:
            src = os.path.join(LOCAL_IMPORT_PATH, f)
            dst = os.path.join(batch_folder, f)

            if os.path.exists(src):
                shutil.move(src, dst)

        log(f"Moved {len(batch_files)} slides to archive")

    elif PROCESSED_FILE_ACTION == "delete":

        deleted = 0

        for f in batch_files:
            src = os.path.join(LOCAL_IMPORT_PATH, f)

            if os.path.exists(src):
                os.remove(src)
                deleted += 1

        log(f"Deleted {deleted} slides from process folder")

    else:
        log("Keeping processed slides in process folder")

    return True
