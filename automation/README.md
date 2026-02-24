# DSA-WSI-DeID Automation Pipeline

This project provides an automated pipeline for processing Whole Slide Images (WSIs) using the SA-WSI-DeID tool. It handles:

- Watching an import folder for `.svs` files
- Generating a manifest
- Ingesting slides into WSI-DeID via API
- Redacting (de-identifying) slides
- Approving and exporting processed slides

All of this can be run automatically, with minimal manual intervention.

---

## Features

- Watch folder automation for `.svs` files
- Automatic manifest creation (`import.xlsx`)
- WSI DeID ingestion, processing, approval, and export via API
- Temporary Girder token handling
- Configurable import/export paths and API keys
- Dockerized WSI-DeID stack support

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

# Docker Installation 
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

## 3. Check running containers
```bash
docker ps
```

You should see containers for:
- girder – WSI-DeID API backend
- worker / redis – background processing
- Other support services as configured


# Configuration

All configurable paths and API keys are in automation/config.py:

```python
# Paths
LOCAL_IMPORT_PATH = "Path to the import folder"
LOCAL_EXPORT_PATH = "Path to the export folder"

# WSI-DeID API
GIRDER_URL = "http://localhost:8080/api/v1"
API_KEY = "PUT_YOUR_TOKEN_HERE"

# Manifest
MANIFEST_FILENAME = "import.xlsx"

# Watcher interval (seconds)
POLL_INTERVAL = 5
```

### Steps to Adjust Config

1. Set LOCAL_IMPORT_PATH to the folder where .svs files will arrive.
2. Set LOCAL_EXPORT_PATH to the folder where processed slides should be saved.
3. Set GIRDER_URL to your WSI-DeID/Girder API endpoint.
4. Generate a Girder API key via your WSI-DeID/Girder admin account and set it as API_KEY.
5. Optionally adjust POLL_INTERVAL to control folder scan frequency.

# Folder Structure

```code
automation/
│   ├─ config.py               # All paths, API key, manifest config
│   ├─ manifest_generator.py   # Scan import folder & generate manifest
│   ├─ wsi_api.py              # API actions: ingest, process, approve, export
│   ├─ pipeline.py             # Single-run pipeline orchestrator
│   └─ watch_folder.py         # Continuous watch folder automation
``