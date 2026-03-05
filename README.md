# Precision Manufacturing Invoice Automations

**Automated invoice processing system built with Python and Claude Code**

This repository contains three invoice processing automations built for Precision Manufacturing Co.'s Finance department, eliminating manual data entry and replacing a process that was taking 10-15 hours per week.

## Project Overview

The Finance team at Precision Manufacturing was drowning in paper invoices. Every invoice had to be opened, read, and manually typed into a spreadsheet. 20+ invoices per day, five fields each, constant typos.

These automations solve that problem at three levels:

- **Batch processing** for clearing backlogs of PDFs
- **Drive monitoring** for hands-free automation of incoming invoices
- **Web portal** for one-off uploads when someone just needs to process a single invoice

**Built with:** Python, pdfplumber, Airtable API, Google Drive API, Flask, Vercel

**Results:**

- 2+ hours saved per day for the Finance team
- 95%+ accuracy in data extraction across 5 different vendor formats
- Fully automated pipeline from PDF upload to database record

## What's Included

### 1. Invoice Processor (Batch)

**Location:** `automations/invoice-processor/`

A Python script that scans a folder of PDF invoices, extracts structured data (invoice number, vendor, dates, amounts), validates the results, and uploads to Airtable.

```bash
python automations/invoice-processor/process_invoices.py
```

**What it does:**

- Reads PDF text with pdfplumber
- Uses regex pattern matching to extract invoice number, vendor name, invoice date, due date, subtotal, tax, and total amount
- Calculates a confidence score based on how many fields were successfully extracted
- Checks for duplicate invoice numbers before uploading
- Moves processed files to an archive folder
- Logs every step for audit trail

### 2. Google Drive Automation

**Location:** `automations/drive-automation/`

A scheduled watcher that monitors a Google Drive folder ("Invoices - To Process") for new PDFs. When one appears, it downloads the file, runs the extraction pipeline, uploads the data to Airtable, and moves the file to "Invoices - Processed".

```bash
# Single check
python automations/drive-automation/drive_invoice_watcher.py --once

# Continuous monitoring (every 5 minutes)
python automations/drive-automation/drive_invoice_watcher.py
```

**What it does:**

- OAuth 2.0 authentication with Google Drive API
- Polls the watch folder for new PDF files
- Downloads to a temp directory, processes, then cleans up
- Moves processed files to archive folder in Drive
- Can run as a cron job via `run_drive_watcher.sh`

### 3. Invoice Upload Web App

**Location:** `automations/invoice-webapp/`

A web application where Finance team members can drag-and-drop a PDF invoice, review the extracted data, edit any fields if needed, and save to Airtable with one click.

**Live at:** https://invoice-webapp-five.vercel.app

**What it does:**

- Drag-and-drop PDF upload interface
- Real-time extraction with confidence score badge
- Editable fields so users can correct any extraction errors before saving
- Duplicate detection warns if the invoice number already exists
- One-click save to Airtable

## Setup Instructions

### Prerequisites

- Python 3.10+
- An Airtable account (free tier works)
- A Google Cloud project with Drive API enabled (for Drive automation only)

### Installation

1. **Clone this repository:**

```bash
git clone https://github.com/tomaibuilder/precision-manufacturing-automations.git
cd precision-manufacturing-automations
```

2. **Create a virtual environment and install dependencies:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Set up environment variables:**

```bash
cp .env.example .env
```

Edit `.env` with your actual Airtable credentials:

```
AIRTABLE_TOKEN=your_personal_access_token
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_TABLE_NAME=Invoices
```

4. **Set up Airtable:**

Create an "Invoices" table with these fields:

| Field Name | Type | Notes |
|---|---|---|
| Invoice Number | Single line text | Primary identifier |
| Vendor | Single line text | Company name |
| Invoice Date | Date | YYYY-MM-DD format |
| Due Date | Date | YYYY-MM-DD format |
| Amount | Currency | Total invoice amount |
| Status | Single select | "Received" or "Under Review" |
| Confidence | Number | 0.0 to 1.0 extraction confidence |
| Notes | Long text | Processing metadata |

5. **Test with sample data:**

```bash
# Copy sample invoices to the input folder
cp sample-data/*.pdf automations/invoice-processor/invoices/
python automations/invoice-processor/process_invoices.py
```

### Google Drive Setup (Optional)

1. Create a Google Cloud project and enable the Drive API
2. Create OAuth 2.0 credentials (Desktop app)
3. Download `credentials.json` to `automations/drive-automation/`
4. Run `python automations/drive-automation/setup_drive_folders.py` to create watch folders
5. Run the watcher: `python automations/drive-automation/drive_invoice_watcher.py --once`

## Sample Data

The `sample-data/` folder contains 5 test invoices from different vendors with varying formats:

| File | Vendor | Invoice # | Amount |
|---|---|---|---|
| invoice-001 | ACME Corp | INV-2024-001 | $15,750.00 |
| invoice-002 | Widget Supplies Direct | WSD-2024-0342 | $3,247.50 |
| invoice-003 | Tech Parts Inc | TPI-20240115 | $8,432.00 |
| invoice-004 | Global Shipping Solutions | GS-2024-1556 | $2,824.20 |
| invoice-005 | Office Depot | OD-884721 | $542.37 |

`expected-output.json` contains the expected extraction results for validation.

## Technical Details

**PDF Text Extraction:** Uses pdfplumber to extract raw text, then applies regex patterns for each field. Multiple patterns per field handle different vendor formats (e.g., "Invoice #:", "Invoice Number:", "INV-").

**Confidence Scoring:** Each invoice gets a confidence score (0.0-1.0) based on how many of the 5 required fields were extracted. Invoices scoring below 0.90 are flagged "Under Review" instead of "Received".

**Duplicate Detection:** Before uploading, the system queries Airtable for existing records with the same invoice number. Duplicates are skipped in batch mode and flagged with a warning in the web app.

## Built With

- **Python** - Core automation logic
- **pdfplumber** - PDF text extraction
- **Airtable API** - Database storage
- **Google Drive API** - File monitoring and management
- **Flask** - Web app backend
- **Vercel** - Web app hosting
- **Claude Code** - AI-assisted development

## Project Structure

```
precision-manufacturing-automations/
├── automations/
│   ├── invoice-processor/
│   │   └── process_invoices.py        # Batch PDF processor
│   ├── drive-automation/
│   │   ├── drive_invoice_watcher.py   # Drive folder monitor
│   │   ├── setup_drive_folders.py     # One-time Drive setup
│   │   └── run_drive_watcher.sh       # Cron wrapper script
│   └── invoice-webapp/
│       ├── app.py                     # Flask backend
│       └── index.html                 # Upload interface
├── sample-data/                       # 5 test invoice PDFs
├── documentation/                     # Complete documentation library
│   ├── DOCUMENTATION.md              # Documentation guide (start here)
│   ├── Handoff_Document.md           # New maintainer onboarding
│   ├── runbooks/                     # Operational guides
│   │   ├── Invoice_Processor_Runbook.md
│   │   ├── Drive_Automation_Runbook.md
│   │   ├── Web_App_Runbook.md
│   │   └── HR_Onboarding_Runbook.md
│   ├── quick-starts/                 # End-user guides
│   │   ├── Invoice_Web_App_Quick_Start.md
│   │   └── HR_Dashboard_Quick_Start.md
│   └── training/                     # Reference materials
│       ├── FAQ.md
│       └── Maintenance_Guide.md
├── .env.example                       # Environment variable template
├── requirements.txt                   # Python dependencies
├── CLAUDE.md                          # Automation playbook
└── README.md                          # This file
```

## Documentation

Complete documentation is available in the `documentation/` folder. See the [Documentation Guide](documentation/DOCUMENTATION.md) for where to start based on your role.

| You are a... | Start with... |
|---|---|
| Finance team member | [Invoice Web App Quick Start](documentation/quick-starts/Invoice_Web_App_Quick_Start.md) |
| HR team member | [HR Dashboard Quick Start](documentation/quick-starts/HR_Dashboard_Quick_Start.md) |
| System operator | [Runbooks](documentation/runbooks/) |
| New maintainer | [Handoff Document](documentation/Handoff_Document.md) |
| Developer | [CLAUDE.md](CLAUDE.md) |

---

_Built as part of the [Claude Code for AI Operators](https://github.com/tomaibuilder/Claude-Code-AI-Operator-Course) course_
