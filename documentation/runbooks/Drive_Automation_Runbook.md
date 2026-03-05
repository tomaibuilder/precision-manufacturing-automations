# Google Drive Invoice Automation - Runbook

## Overview

**What it does:** Monitors a Google Drive folder for new invoice PDFs. When a new file appears, it automatically downloads, extracts data, uploads to Airtable, and moves the file to a "Processed" folder.

**Why it exists:** Suppliers and vendors email invoices that Finance uploads to Google Drive. This automation eliminates the manual step of downloading, opening, and entering invoice data.

**Who uses it:** Finance team uploads PDFs to Drive. The automation handles the rest.

**Impact:** Zero manual intervention needed. Invoices are processed within minutes of upload.

---

## Setup & Prerequisites

### Software Required

- Python 3.10+
- Google account with Drive access
- Google Cloud Console project with Drive API enabled

### Python Packages

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib pdfplumber requests python-dotenv
```

### Credentials Required

| Credential | Where to Get It | Where It's Stored |
|-----------|----------------|-------------------|
| Google OAuth credentials | Google Cloud Console > APIs > Credentials | `credentials.json` |
| Google OAuth token | Generated on first run (browser auth) | `token.json` |
| Airtable Token | https://airtable.com/create/tokens | `.env` file |
| Airtable Base ID | URL bar when viewing base | `.env` file |

### First-Time Google Setup

1. Go to https://console.cloud.google.com
2. Create a new project (or use existing)
3. Enable the Google Drive API
4. Create OAuth 2.0 credentials (Desktop app type)
5. Download `credentials.json` to `drive-watcher/` folder
6. On first run, a browser window opens for authentication
7. After login, `token.json` is created automatically

### Drive Folder Structure

The automation uses two folders in Google Drive:

```
My Drive/
└── Precision Manufacturing/
    └── Finance/
        ├── Invoices - To Process/    <-- Upload new PDFs here
        └── Invoices - Processed/     <-- Automation moves files here
```

Run the setup script to create these folders:
```bash
python setup_drive_folders.py
```

Folder IDs are stored in `drive_config.json`.

---

## How to Run It

### Continuous Mode (Recommended)

Watches for new files and processes them automatically:

```bash
cd /path/to/invoice-automation/drive-watcher
source ../venv/bin/activate
python drive_invoice_watcher.py
```

Output:
```
Drive Invoice Watcher started.
Watching folder: Invoices - To Process
Checking every 5 minutes...

[14:30:02] Checking for new files...
[14:30:03] Found: invoice-march-acme.pdf
[14:30:04] Downloaded to temp_downloads/
[14:30:05] Extracted: Acme Corp, INV-2024-0891, $3,450.00
[14:30:06] Uploaded to Airtable.
[14:30:06] Moved to Invoices - Processed.
[14:35:02] Checking for new files... No new files.
```

### Single Check Mode

Process any waiting files, then exit:

```bash
python drive_invoice_watcher.py --once
```

### Using the Shell Script

```bash
./run_drive_watcher.sh
```

### How to Stop

Press `Ctrl+C` to stop the watcher.

### How to Pause Without Stopping

Simply don't upload files to the "To Process" folder. The watcher checks but finds nothing.

---

## What Could Go Wrong

### Error: "credentials.json not found"
**Fix:** Download OAuth credentials from Google Cloud Console and place in the `drive-watcher/` folder.

### Error: "Token expired"
**Fix:** Delete `token.json` and run again. A browser window will open for re-authentication.

### Error: "Folder not found"
**Fix:** Run `python setup_drive_folders.py` to recreate the folder structure. Or check `drive_config.json` has valid folder IDs.

### Files Not Being Detected
**Cause:** File uploaded to wrong folder, or not a PDF
**Fix:** Verify files are in "Invoices - To Process" folder (not a subfolder). Only `.pdf` files are processed.

### Error: "Permission denied"
**Fix:** Ensure the Google account used for OAuth has edit access to the Drive folders.

---

## Monitoring & Verification

### Check Logs

```bash
cat logs/drive_watcher.log
```

### Verify Processing

1. Upload a test PDF to "Invoices - To Process" in Drive
2. Wait up to 5 minutes (or run with `--once`)
3. Check that the file moved to "Invoices - Processed"
4. Verify the record appeared in Airtable

### Check the Watcher Is Running

If running in background:
```bash
ps aux | grep drive_invoice_watcher
```

---

## Maintenance

### Monthly

- Check `token.json` is still valid (Google OAuth tokens can expire)
- Review `logs/drive_watcher.log` for recurring errors
- Clean up `temp_downloads/` folder

### Quarterly

- Review Google Cloud Console for API usage
- Check Drive storage usage in the Processed folder
- Test with a sample invoice to verify accuracy

### If Google Changes Their API

- Update `google-api-python-client` package
- Check Google's migration guides
- Test thoroughly before deploying changes

---

## Emergency Procedures

### Watcher Stopped and Invoices Are Waiting

1. Start the watcher: `python drive_invoice_watcher.py --once`
2. It will process all waiting files
3. Restart continuous mode if needed

### Manual Fallback

If the Drive watcher is broken:
1. Download PDFs from Drive manually
2. Place them in the `invoices/` folder
3. Run the batch processor: `python scripts/process_invoices.py`

### Contact

- **Maintainer:** [AI Operations Lead]
- **Google Admin:** [IT team]
- **Escalation:** [Manager name]
