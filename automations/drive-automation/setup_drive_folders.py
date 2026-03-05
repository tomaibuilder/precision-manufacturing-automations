#!/usr/bin/env python3
"""Create the 'Invoices - To Process' and 'Invoices - Processed' folders in Google Drive."""

import os, json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, 'token.json')
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return build('drive', 'v3', credentials=creds)


def create_folder(service, name):
    metadata = {'name': name, 'mimeType': 'application/vnd.google-apps.folder'}
    folder = service.files().create(body=metadata, fields='id, name').execute()
    return folder['id']


def main():
    service = get_service()

    to_process_id = create_folder(service, 'Invoices - To Process')
    print(f"Created 'Invoices - To Process'  -> ID: {to_process_id}")

    processed_id = create_folder(service, 'Invoices - Processed')
    print(f"Created 'Invoices - Processed'   -> ID: {processed_id}")

    # Save folder IDs to config
    config = {
        'to_process_folder_id': to_process_id,
        'processed_folder_id': processed_id,
    }
    config_path = os.path.join(SCRIPT_DIR, 'drive_config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\nFolder IDs saved to: {config_path}")
    print("Open Google Drive to verify the folders exist.")


if __name__ == '__main__':
    main()
