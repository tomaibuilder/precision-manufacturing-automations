# Invoice Processing Automation - Runbook

## Overview

**What it does:** Extracts invoice data (vendor, amounts, dates, line items) from PDF files and saves structured records to Airtable automatically.

**Why it exists:** Finance was manually entering 20+ invoices per day into spreadsheets. Each invoice took 5-10 minutes. This automation processes a batch of PDFs in under 30 seconds with 95%+ accuracy.

**Who uses it:** Finance team (Sarah's department)

**Impact:** Saves ~15-20 hours/month in manual data entry. Eliminates transcription errors.

---

## Setup & Prerequisites

### Software Required

- Python 3.10+
- pip (Python package manager)

### Python Packages

```bash
pip install pdfplumber requests python-dotenv
```

### Credentials Required

| Credential | Where to Get It | Where It's Stored |
|-----------|----------------|-------------------|
| Airtable Personal Access Token | https://airtable.com/create/tokens | `.env` file |
| Airtable Base ID | URL bar when viewing your base | `.env` file |

### .env File Setup

Create a `.env` file in the `invoice-automation/` directory:

```
AIRTABLE_TOKEN=your_personal_access_token
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_TABLE_NAME=Invoices
```

### Airtable Table Schema

The "Invoices" table must have these fields:

| Field Name | Type | Notes |
|-----------|------|-------|
| Invoice Number | Single line text | Primary field |
| Vendor Name | Single line text | |
| Invoice Date | Date | |
| Due Date | Date | |
| Subtotal | Currency | |
| Tax | Currency | |
| Total Amount | Currency | |
| Line Items | Long text | JSON string |
| Confidence Score | Number (decimal) | 0.0 to 1.0 |
| Source File | Single line text | Original PDF filename |
| Status | Single select | Pending / Reviewed / Approved |

---

## How to Run It

### Batch Processing (Most Common)

1. **Place PDF invoices** in the `invoices/` folder:
   ```
   invoice-automation/invoices/
   ```

2. **Run the processor:**
   ```bash
   cd /path/to/invoice-automation
   source venv/bin/activate
   python scripts/process_invoices.py
   ```

3. **What you'll see:**
   ```
   Processing invoice-001-acme-corp.pdf...
     Vendor: Acme Corp
     Invoice #: INV-2024-0342
     Total: $1,242.00
     Confidence: 0.98
     Uploaded to Airtable successfully.

   Processing invoice-002-widget-supplies.pdf...
     ...

   Done! Processed 5 invoices. 5 successful, 0 failed.
   ```

4. **After processing:**
   - Processed PDFs move to `processed/` folder
   - Data appears in Airtable within seconds
   - Log file updated at `logs/processing.log`

### How Long It Takes

- ~2-3 seconds per invoice
- Batch of 20 invoices: under 1 minute
- Network-dependent (Airtable API calls)

### What Success Looks Like

- All PDFs moved from `invoices/` to `processed/`
- New rows appear in Airtable with extracted data
- Confidence scores above 0.85 for standard invoices
- No ERROR lines in `logs/processing.log`

---

## What Could Go Wrong

### Error: "No .env file found"
**Cause:** Missing `.env` file
**Fix:** Create `.env` with Airtable credentials (see Setup section)

### Error: "AIRTABLE_TOKEN not set"
**Cause:** Empty or missing token in `.env`
**Fix:** Check `.env` file has valid token. Get a new one at https://airtable.com/create/tokens

### Error: "Duplicate invoice: INV-XXXX"
**Cause:** Invoice already exists in Airtable
**Fix:** This is expected behavior. The script skips duplicates to prevent double-entry. If you need to reprocess, delete the record from Airtable first.

### Error: "Could not extract text from PDF"
**Cause:** PDF is scanned/image-based (not text-based)
**Fix:** This processor works with text-based PDFs only. For scanned invoices, the PDF needs to be OCR'd first using a tool like Adobe Acrobat.

### Low confidence score (below 0.7)
**Cause:** Invoice format doesn't match expected patterns
**Fix:** Review the extracted data manually in Airtable. The automation uses regex patterns tuned for common invoice formats. Unusual layouts may need manual review.

### Error: "Rate limit exceeded"
**Cause:** Too many Airtable API calls too quickly
**Fix:** Wait 30 seconds and run again. Airtable allows 5 requests/second. For large batches (100+), the script includes built-in delays.

---

## Monitoring & Verification

### Check Processing Log

```bash
cat logs/processing.log
```

Look for:
- `SUCCESS` lines: Invoice processed and uploaded
- `SKIP` lines: Duplicate invoice skipped
- `ERROR` lines: Something went wrong (check details)

### Verify in Airtable

1. Open your Airtable base
2. Go to the "Invoices" table
3. Sort by "Created" (newest first)
4. Verify new records match the PDFs you processed

### Spot-Check Data Quality

Pick 2-3 invoices and compare:
- Does the total amount match the PDF?
- Is the vendor name correct?
- Are dates formatted properly?

---

## Maintenance

### Monthly

- **Update Python packages:**
  ```bash
  cd /path/to/invoice-automation
  source venv/bin/activate
  pip install --upgrade pdfplumber requests
  ```
- **Clear old logs:** Archive `logs/processing.log` if it exceeds 1MB
- **Review processed folder:** Archive or delete old PDFs from `processed/`

### Quarterly

- **Test with sample invoices:** Run the 5 test invoices in `test_data/` to verify accuracy
- **Check Airtable API token:** Tokens can expire. Regenerate if needed.
- **Review confidence scores:** If scores are trending down, new vendor formats may need pattern updates

### When Updating the Script

1. Test changes with sample data first (`test_data/` folder)
2. Compare output against `test_data/expected-output.json`
3. If results match, deploy changes

---

## Emergency Procedures

### Automation Is Broken and Invoices Need Processing

**Manual fallback:** Enter invoices directly into Airtable by hand. This is what Finance did before the automation existed.

1. Open the PDF
2. Copy relevant fields into Airtable manually
3. Mark Status as "Manual Entry"
4. Log the issue for the maintainer

### Script Won't Start

```bash
# Check Python is installed
python3 --version

# Check virtual environment exists
ls venv/

# Recreate if needed
python3 -m venv venv
source venv/bin/activate
pip install pdfplumber requests python-dotenv
```

### Airtable Is Down

- Check https://status.airtable.com
- PDFs will stay in `invoices/` folder until reprocessed
- No data is lost - just run the script again when Airtable is back

### Contact

- **Maintainer:** [AI Operations Lead]
- **Airtable Admin:** [Admin name]
- **Escalation:** [Manager name]
