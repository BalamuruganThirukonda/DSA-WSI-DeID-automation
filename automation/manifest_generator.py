import re
import os
import hashlib
import pandas as pd
from automation.config import LOCAL_IMPORT_PATH, MANIFEST_FILENAME

# =====================================
# PSEUDONYM GENERATOR
# =====================================
def generate_pseudoname(real_id):
    """
    Deterministic pseudoname from real case ID.
    Same input -> same output.
    Uses letters + numbers for uniqueness.
    """
    hash_object = hashlib.sha256(real_id.encode())
    hash_int = int(hash_object.hexdigest(), 16)
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    num_part = hash_int % 10000  # 4-digit number
    letter_part = letters[(hash_int // 10000) % 26]
    return f"{letter_part}{num_part:04d}"

# =====================================
# FILENAME PARSER
# =====================================
def parse_filename(filename):
    """
    Parse the SVS filename to extract:
    - TokenID / PatientID (first 11 characters)
    - SampleID = CPH-pseudonym-G-1-2-KI-67
    """
    name = os.path.splitext(filename)[0]

    # Pattern:
    # (E/T/R + 10 digits)
    # S + letter
    # -block-section-stain
    pattern = r'^([ETR]\d{10})S([A-Z])-(\d+)-(\d+)-(.+?)(?:_UTC.*)?$'
    match = re.match(pattern, name)

    if not match:
        # fallback
        token_patient = name[:11]
        pseudo = generate_pseudoname(token_patient)
        return {
            "TokenID": token_patient,
            "PatientID": token_patient,
            "SampleID": f"CPH-{pseudo}-UNKNOWN"
        }

    token_patient = match.group(1)   # E2025024494
    letter = match.group(2)          # G
    block = match.group(3)           # 1
    section = match.group(4)         # 2
    stain = match.group(5)           # KI-67

    # Deterministic pseudonym based on PatientID only
    pseudo = generate_pseudoname(token_patient)

    sample_id = f"CPH-{pseudo}-{letter}-{block}-{section}-{stain}"

    return {
        "TokenID": token_patient,
        "PatientID": token_patient,
        "SampleID": sample_id
    }

# =====================================
# MANIFEST GENERATOR
# =====================================
def generate_manifest(batch_files=None, manifest_path=None):
    """
    Generate manifest Excel file for SVS files.
    If batch_files is provided, only those files are used.
    """

    # Default manifest path
    if manifest_path is None:
        manifest_path = os.path.join(LOCAL_IMPORT_PATH, MANIFEST_FILENAME)

    # Determine which files to process
    if batch_files is None:
        svs_files = [
            f for f in os.listdir(LOCAL_IMPORT_PATH)
            if f.lower().endswith(".svs")
        ]
    else:
        svs_files = batch_files

    if not svs_files:
        print("No SVS files found.")
        return False

    print(f"Scanning for SVS files in import folder: {LOCAL_IMPORT_PATH}")
    print(f"Found {len(svs_files)} SVS files.")

    rows = []

    for i, file in enumerate(svs_files, start=1):
        parsed = parse_filename(file)

        rows.append({
            "TokenID": parsed["TokenID"],
            "Proc_Seq": i,
            "Slide_ID": i,
            "InputFileName": file,
            "SampleID": parsed["SampleID"],
            "PatientID": parsed["PatientID"]
        })

    df = pd.DataFrame(rows)

    df.to_excel(manifest_path, index=False)

    print("\nManifest generated successfully:", manifest_path)

    return True

# =====================================
# MAIN
# =====================================
if __name__ == "__main__":
    generate_manifest()
