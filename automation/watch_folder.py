import os
import time
from datetime import datetime
from automation.pipeline import run_test_pipeline
from automation.config import IMPORT_FOLDER, POLL_INTERVAL

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def import_has_files():
    """Check if Import folder contains SVS/NDPI files."""
    for root, _, files in os.walk(IMPORT_FOLDER):
        for f in files:
            if f.lower().endswith((".svs", ".ndpi")):
                return True
    return False

def main_loop():
    log(f"Watching {IMPORT_FOLDER} every {POLL_INTERVAL} seconds...")

    while True:
        try:
            if import_has_files():
                log("New slides detected. Starting pipeline batch...")
                run_test_pipeline()  # pipeline handles moving batch internally
            else:
                log("No new WSI files found in Import folder.")

            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            log("Stopped by user.")
            break

if __name__ == "__main__":
    main_loop()
