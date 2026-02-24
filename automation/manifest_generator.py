# manifest_generator.py
import re
import os
import pandas as pd
from config import LOCAL_IMPORT_PATH, MANIFEST_FILENAME

# =====================================
# FILENAME PARSER
# =====================================
def parse_filename(filename):
    """
    Parse the SVS filename to extract:
    - TokenID / PatientID
    - SampleID according to your rules
    """
    name = os.path.splitext(filename)[0]

    # Pattern matches:
    # E/T/R + 10 digits -> TokenID / PatientID
    # SA/SB block
    # -block-section
    # -stain (before _UTC or end)
    pattern = r'^([ETR]\d{10})(S[AB])-(\d+)-(\d+)-(.+?)(?:_UTC.*)?$'
    match = re.match(pattern, name)

    if not match:
        # fallback rule: use filename as SampleID with -DeID
        return {
            "TokenID": name,
            "PatientID": name,
            "SampleID": name + "-DeID"
        }

    full_id = match.group(1)          # E2025001234
    sa_block = match.group(2)         # SA or SB
    block = match.group(3)
    section = match.group(4)
    stain = match.group(5)            # H&E, KI-67, etc.

    case_6digit = full_id[-6:]        # last 6 digits
    letter = sa_block[-1]             # A or B

    sample_id = f"CPH-{case_6digit}-{letter}{block}-{section}-{stain}-DeID"

    return {
        "TokenID": full_id,
        "PatientID": full_id,
        "SampleID": sample_id
    }

# =====================================
# MANIFEST GENERATOR
# =====================================
def generate_manifest():
    """
    Scan the import folder for .svs files and generate an Excel manifest
    """
    print("\nScanning for SVS files in import folder:", LOCAL_IMPORT_PATH)

    files = [f for f in os.listdir(LOCAL_IMPORT_PATH) if f.lower().endswith(".svs")]

    if not files:
        print("No .svs files found. Place SVS files in the import folder.")
        return False

    print(f"Found {len(files)} SVS files.")

    rows = []
    for i, file in enumerate(files, start=1):
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

    manifest_path = os.path.join(LOCAL_IMPORT_PATH, MANIFEST_FILENAME)
    df.to_excel(manifest_path, index=False)

    print("\nManifest generated successfully:", manifest_path)
    return True

# =====================================
# MAIN
# =====================================
if __name__ == "__main__":
    generate_manifest()