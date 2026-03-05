#!/usr/bin/env python3
"""
Drive Invoice Watcher
Watches a Google Drive folder for new PDF invoices, downloads them,
processes with invoice_processor.py, and moves to a Processed folder.

Usage:
    python3 drive_invoice_watcher.py --once     # Single check
    python3 drive_invoice_watcher.py            # Continuous (every 5 min)
"""

import os
import sys
import json
import time
import shutil
import logging
import argparse
import tempfile
import io
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # invoice-automation/

# Add scripts/ to path so we can import process_invoices
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'scripts'))

CREDS_FILE = os.path.join(SCRIPT_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(SCRIPT_DIR, 'token.json')
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'drive_config.json')
LOG_FILE = os.path.join(PROJECT_ROOT, 'logs', 'drive_watcher.log')
TEMP_DIR = os.path.join(SCRIPT_DIR, 'temp_downloads')

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CHECK_INTERVAL = 300  # 5 minutes

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def load_config():
    """Load Drive folder IDs from config file."""
    if not os.path.exists(CONFIG_FILE):
        logger.error(f"Config file not found: {CONFIG_FILE}")
        logger.error("Run setup_drive_folders.py first.")
        sys.exit(1)

    with open(CONFIG_FILE) as f:
        config = json.load(f)

    required = ['to_process_folder_id', 'processed_folder_id']
    for key in required:
        if not config.get(key):
            logger.error(f"Missing config key: {key}")
            sys.exit(1)

    return config

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def authenticate():
    """Authenticate with Google Drive, refreshing token if needed."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired token...")
            creds.refresh(Request())
        else:
            logger.info("Starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
        logger.info("Token saved.")

    return build('drive', 'v3', credentials=creds)

# ---------------------------------------------------------------------------
# Drive Operations
# ---------------------------------------------------------------------------

def list_pdfs_in_folder(service, folder_id):
    """List all PDF files in a Drive folder."""
    query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
    results = service.files().list(
        q=query,
        fields="files(id, name, createdTime)",
        orderBy="createdTime",
    ).execute()
    return results.get('files', [])


def download_file(service, file_id, filename):
    """Download a file from Drive to the temp directory."""
    dest_path = os.path.join(TEMP_DIR, filename)
    request = service.files().get_media(fileId=file_id)
    with open(dest_path, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                logger.info(f"  Download progress: {int(status.progress() * 100)}%")
    logger.info(f"  Downloaded: {filename}")
    return dest_path


def move_file_to_folder(service, file_id, new_folder_id):
    """Move a file from one Drive folder to another."""
    # Get current parents
    file = service.files().get(fileId=file_id, fields='parents').execute()
    previous_parents = ",".join(file.get('parents', []))

    # Move to new folder
    service.files().update(
        fileId=file_id,
        addParents=new_folder_id,
        removeParents=previous_parents,
        fields='id, parents',
    ).execute()
    logger.info(f"  Moved to Processed folder in Drive")

# ---------------------------------------------------------------------------
# Invoice Processing (uses existing pipeline)
# ---------------------------------------------------------------------------

def process_downloaded_invoice(pdf_path):
    """
    Process a downloaded PDF using the existing invoice processor.
    Returns True if successful, False otherwise.
    """
    try:
        from process_invoices import (
            read_pdf, extract_invoice_data, validate_invoice,
            check_duplicate, upload_to_airtable
        )
    except ImportError as e:
        logger.error(f"Cannot import invoice processor: {e}")
        logger.error("Make sure process_invoices.py is in scripts/")
        return False

    # Read PDF
    text = read_pdf(pdf_path)
    if text is None:
        logger.error(f"  Failed to read PDF: {os.path.basename(pdf_path)}")
        return False

    # Extract data
    data = extract_invoice_data(text)

    # Check duplicate
    inv_num = data.get('invoice_number')
    if inv_num and check_duplicate(inv_num):
        logger.info(f"  Duplicate invoice {inv_num} - skipping upload")
        return True  # Not a failure, just already exists

    # Upload to Airtable
    if not upload_to_airtable(data):
        logger.error(f"  Failed to upload to Airtable")
        return False

    logger.info(f"  Invoice processed and uploaded to Airtable")
    return True

# ---------------------------------------------------------------------------
# Main Watcher Logic
# ---------------------------------------------------------------------------

def check_and_process(service, config):
    """One check cycle: list files, download, process, move."""
    folder_id = config['to_process_folder_id']
    processed_folder_id = config['processed_folder_id']

    logger.info("Checking for new invoices in Drive...")
    files = list_pdfs_in_folder(service, folder_id)

    if not files:
        logger.info("No new PDFs found.")
        return 0

    logger.info(f"Found {len(files)} PDF(s) to process.")
    processed_count = 0

    for file_info in files:
        file_id = file_info['id']
        filename = file_info['name']
        logger.info(f"\n--- Processing: {filename} ---")

        try:
            # Download
            pdf_path = download_file(service, file_id, filename)

            # Process
            success = process_downloaded_invoice(pdf_path)

            if success:
                # Move in Drive
                move_file_to_folder(service, file_id, processed_folder_id)
                processed_count += 1
            else:
                logger.warning(f"  {filename} failed processing - leaving in To Process folder")

        except Exception as e:
            logger.error(f"  Error processing {filename}: {e}")

        finally:
            # Clean up temp file
            temp_path = os.path.join(TEMP_DIR, filename)
            if os.path.exists(temp_path):
                os.remove(temp_path)

    logger.info(f"\nProcessed {processed_count}/{len(files)} invoices.")
    return processed_count


def run_watcher(once=False):
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("DRIVE INVOICE WATCHER - Starting")
    logger.info("=" * 60)

    config = load_config()
    service = authenticate()

    logger.info(f"To Process folder: {config['to_process_folder_id']}")
    logger.info(f"Processed folder:  {config['processed_folder_id']}")

    if once:
        logger.info("Mode: single check")
        check_and_process(service, config)
        logger.info("Done.")
        return

    logger.info(f"Mode: continuous (checking every {CHECK_INTERVAL}s)")
    try:
        while True:
            check_and_process(service, config)
            logger.info(f"Next check in {CHECK_INTERVAL // 60} minutes...")
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        logger.info("\nStopped by user (Ctrl+C).")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Watch Google Drive for invoice PDFs')
    parser.add_argument('--once', action='store_true', help='Run once then exit')
    args = parser.parse_args()

    run_watcher(once=args.once)
