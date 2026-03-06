# Paths for local testing
IMPORT_FOLDER = "/home/thirukondabalamurugan/Desktop/CPHGPU1-Slides/DeID/DeID-Import"
LOCAL_IMPORT_PATH = "/home/thirukondabalamurugan/Desktop/CPHGPU1-Slides/DeID/Process"
LOCAL_EXPORT_PATH = "/home/thirukondabalamurugan/Desktop/CPHGPU1-Slides/DeID/DeID-Export"

PROCESS_FOLDER = "/home/thirukondabalamurugan/Desktop/CPHGPU1-Slides/DeID/Process"

DB_FILE = "data/processed_files.db"
DB_EXCEL_FOLDER = "/home/thirukondabalamurugan/Desktop/CPHGPU1-Slides/DeID"

# WSI DeID / Girder API
GIRDER_URL = "http://localhost:8080/api/v1"
API_KEY = "API_KEY"  # Replace this with your Girder API key

# Manifest file name (generated in import folder)
MANIFEST_FILENAME = "import.xlsx"

# Folder polling interval (used for watch_folder.py)
POLL_INTERVAL = 120  # seconds

# Batch processing
BATCH_SIZE = 20

# ---------------------------------------
# Post-processing behaviour
# ---------------------------------------

# What to do with slides after processing
# Options: "move", "delete", "keep"
PROCESSED_FILE_ACTION = "delete"
ARCHIVE_FOLDER = "/home/thirukondabalamurugan/Desktop/CPHGPU1-Slides/DeID/Archive"

# Delete DeID Export Job excel files
DELETE_EXPORT_JOB_FILES = True

