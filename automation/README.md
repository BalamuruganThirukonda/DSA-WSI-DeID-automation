# DSA-WSI-DeID Automation Pipeline

This project provides an automated pipeline for processing Whole Slide Images (WSIs) using the DSA-WSI-DeID tool.

The automation continuously monitors an Import folder, processes slides in batches, sends them to the WSI-DeID system via API, exports the de-identified slides, logs processing history, and manages processed files automatically.

The goal is to run the entire DeID workflow without manual intervention.

---

## Features

- Automatic watch folder pipeline

- Batch processing of .svs slides

- Automatic manifest generation

- Automatic ingest → redact → approve → export

- Handles slides inside nested subfolders

- Prevents processing partially copied files

- Automatic database logging of processed slides

- Optional archive or deletion of processed slides

- Automatic removal of DeID Export Job Excel files

- Configurable paths and batch sizes

- Compatible with Dockerized WSI-DeID stack

---

## Workflow Overview

The pipeline performs the following steps automatically:

- Detect new slides in the Import folder

- Move slides to the Process folder

- Generate a manifest file

- Ingest slides into Girder / WSI-DeID

- Redact (de-identify) slides

- Approve processed slides

- Export de-identified slides

- Clean up temporary export files

- Delete processed items from Girder

- Log processed slides to database

- Archive or delete processed slides

---
## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-org/DSA-WSI-DeID.git
cd DSA-WSI-DeID
```

### 2. Set up Python environment

```bash
python3 -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```
Ensure pandas, request, watchdog and openpyxl are installed.

---

# Docker Installation (WSI-DeID)
The WSI-DeID tool is packaged as Docker containers. Follow these steps:

## 1. Install Docker
- Windows / macOS: Docker Desktop
- Linux: Docker Engine

Verify installation:
```bash
docker --version
docker-compose --version
```

## 2. Start WSI-DeID stack
Navigate to the devops folder:

```bash
cd devops/wsi_deid
docker-compose -f docker-compose.local.yml up -d
```

This will start the Girder server and WSI-DeID services in Docker containers.

Default API URL: http://localhost:8080/api/v1

## 3. Verify running containers
```bash
docker ps
```

You should see containers for:
- girder – WSI-DeID API backend
- worker / redis – background processing
- Other support services as configured

---
# Configuration

All settings are controlled in:
```
automation/config.py
```
Example configuration:

```python
# Import / Process folders
IMPORT_FOLDER = "/data/import"
LOCAL_IMPORT_PATH = "/data/process"

# Export folder
LOCAL_EXPORT_PATH = "/data/export"

# Archive folder
ARCHIVE_FOLDER = "/data/archive"

# WSI-DeID API
GIRDER_URL = "http://localhost:8080/api/v1"
API_KEY = "PUT_YOUR_TOKEN_HERE"

# Manifest
MANIFEST_FILENAME = "import.xlsx"

# Batch processing
BATCH_SIZE = 20

# Processed file handling
PROCESSED_FILE_ACTION = "delete" # options: move | delete | keep
# Delete DeID Export Job Excel files
DELETE_EXPORT_JOB_FILES = True

# Watch interval (seconds)
POLL_INTERVAL = 5
```

### Configuration Steps

1. Set IMPORT_FOLDER where new .svs slides arrive.
2. Set LOCAL_IMPORT_PATH as the processing folder.
3. Set LOCAL_EXPORT_PATH where de-identified slides will be exported.
4. Set ARCHIVE_FOLDER if you plan to archive processed slides.
5. Set GIRDER_URL to your WSI-DeID API endpoint.
6. Generate a Girder API key and add it as API_KEY.
7. Adjust BATCH_SIZE depending on server capacity.
---
# Folder Structure

```code
automation/
│   ├─ config.py               # All paths, API key, manifest config
│   ├─ manifest_generator.py   # Scan import folder & generate manifest
│   ├─ wsi_api.py              # API actions: ingest, process, approve, export
│   ├─ pipeline.py             # Single-run pipeline orchestrator
│   ├─ watch_folder.py         # Continuous watch folder automation
    └─ db_logger.py
```
---
# Running the Automation


Start the watch-folder automation:
```
python automation/watch_folder.py
```
The system will continuously:
- Scan the Import folder
- Move slides to the Process folder
- Run the DeID pipeline
- Repeat automatically

---
# License
