
import os
import pandas as pd
from datetime import datetime
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

DB_FILE = os.path.join(PROJECT_ROOT, "data", "processed_files.db")

DB_EXCEL_FOLDER = "/home/thirukondabalamurugan/Desktop/CPHGPU1-Slides/DeID"

def initialize_database():
    """
    Create database and table if not exists.
    """
    db_folder = os.path.dirname(DB_FILE)
    os.makedirs(db_folder, exist_ok=True)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_filename TEXT NOT NULL,
            pseudonym_filename TEXT NOT NULL,
            processed_time TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def insert_processed_files(df: pd.DataFrame):
    """
    Insert processed files into DB.
    Expects dataframe with:
        - InputFileName
        - SampleID
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO processed_files (
                original_filename,
                pseudonym_filename,
                processed_time
            )
            VALUES (?, ?, ?)
        """, (
            row["InputFileName"],      # Original filename
            row["SampleID"],           # Pseudonym filename
            current_time
        ))

    conn.commit()
    conn.close()


def export_history_to_excel(output_folder=None):
    if output_folder is None:
        output_folder = DB_EXCEL_FOLDER

    print(f"[Export] Saving Excel to: {output_folder}")

    os.makedirs(output_folder, exist_ok=True)

    excel_path = os.path.join(output_folder, "DeID_Filename_Mapping.xlsx")

    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM processed_files", conn)

        if df.empty:
            print("[Export] No records found in database.")
        else:
            df.to_excel(excel_path, index=False)
            print(f"[Export] File saved successfully: {excel_path}")

    except Exception as e:
        print(f"[Export] Error: {e}")
        excel_path = None
    finally:
        conn.close()

    return excel_path
