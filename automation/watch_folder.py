# automation/watch_folder.py
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pipeline import run_pipeline
from config import LOCAL_IMPORT_PATH, POLL_INTERVAL, MANIFEST_FILENAME
import os

class SVSHandler(FileSystemEventHandler):
    """
    Watchdog event handler for new SVS files.
    """
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(".svs"):
            print(f"\n[+] New SVS detected: {event.src_path}")
            # Check if manifest already exists; remove it to regenerate
            manifest_path = os.path.join(LOCAL_IMPORT_PATH, MANIFEST_FILENAME)
            if os.path.exists(manifest_path):
                os.remove(manifest_path)
                print(f"[i] Existing manifest removed: {manifest_path}")

            # Run the full pipeline
            run_pipeline()

if __name__ == "__main__":
    print(f"Watching import folder: {LOCAL_IMPORT_PATH}")
    event_handler = SVSHandler()
    observer = Observer()
    observer.schedule(event_handler, path=LOCAL_IMPORT_PATH, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        observer.stop()
        print("\nWatcher stopped by user.")
    observer.join()