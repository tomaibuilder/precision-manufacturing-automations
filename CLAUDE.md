# Invoice Automation Playbook

**Context and decisions for anyone maintaining or extending these automations.**

---

## Why This Exists

Precision Manufacturing's Finance department was manually processing 20+ invoices per day. Each invoice required opening the PDF, reading 5-7 fields, and typing them into a tracking system. This took 10-15 hours per week and produced frequent data entry errors.

The goal was to automate this end-to-end: PDF in, structured data out, stored in Airtable.

## Architecture Decisions

### Why pdfplumber (not OCR)

The invoices are digital PDFs with embedded text, not scanned images. pdfplumber extracts text directly without needing OCR (Tesseract, etc.). This is faster, more reliable, and has zero dependencies on external services.

If scanned/image-based PDFs become common, the extraction layer would need to swap pdfplumber for an OCR solution.

### Why regex (not AI extraction)

The invoice formats are predictable. Five vendors, consistent layouts. Regex pattern matching handles this well and costs nothing to run. An LLM-based extractor would be more flexible but adds cost and latency for a problem that doesn't need it.

The extraction functions use multiple patterns per field with fallback logic. For example, `extract_invoice_number()` tries 5 different patterns before giving up.

### Why Airtable (not a database)

Airtable gives the Finance team a familiar spreadsheet-like interface to view and manage records. No SQL knowledge needed. The REST API is simple. The free tier handles the volume.

### Why Flask (not FastAPI/Django)

The web app is a single-page upload tool. Flask is the simplest option. No ORM, no auth, no sessions needed.

## Key Technical Patterns

### Confidence Scoring

Every extraction produces a confidence score: `fields_found / fields_required`. If the score is below 0.90 (i.e., at least one required field is missing), the record gets status "Under Review" instead of "Received". This lets the Finance team quickly filter for invoices that need manual attention.

### Duplicate Prevention

Before uploading to Airtable, the system queries for existing records with the same invoice number. In batch mode, duplicates are silently skipped. In the web app, a warning is displayed but the user can still save if they choose.

### File Lifecycle

1. PDF arrives (in folder, Drive, or via upload)
2. Text extracted with pdfplumber
3. Data extracted with regex patterns
4. Validated (confidence score calculated)
5. Duplicate check against Airtable
6. Upload to Airtable
7. File moved to processed/archive folder

## Known Limitations

- **invoice-003** (Tech Parts Inc) produces garbled HTML in the extracted text. The extractor still pulls the right data, but the raw text is messy. This is a PDF generation issue on the vendor's side.
- Only handles digital PDFs. Scanned image PDFs will return no text.
- Regex patterns are tuned for the 5 sample vendors. New vendor formats may need new patterns added.
- The Drive watcher polls every 5 minutes. There is no real-time webhook trigger.

## Environment Setup

All credentials are stored in environment variables (never hardcoded):

```
AIRTABLE_TOKEN     - Airtable Personal Access Token
AIRTABLE_BASE_ID   - Airtable Base ID
AIRTABLE_TABLE_NAME - Table name (default: "Invoices")
```

Google Drive authentication uses OAuth 2.0 with a `credentials.json` file (not committed to git). Running the watcher for the first time triggers a browser-based auth flow that saves a `token.json` locally.

## Extending This System

### Adding a new vendor format

1. Get a sample invoice PDF from the vendor
2. Run `pdfplumber` on it to see the raw text
3. Check if existing patterns match
4. If not, add new regex patterns to the relevant `extract_*` functions in `process_invoices.py`
5. Add the sample PDF to `sample-data/` and update `expected-output.json`

### Adding new fields

1. Add the extraction function in `process_invoices.py`
2. Add the field to `extract_invoice_data()`
3. Add the field to the Airtable table schema
4. Update the web app frontend to display the new field

### Running as a cron job

The Drive watcher can run on a schedule:

```bash
# Check every 15 minutes
*/15 * * * * /path/to/run_drive_watcher.sh >> /path/to/logs/cron.log 2>&1
```

## Port Notes

- macOS reserves port 5000 for AirPlay Receiver. The Flask dev server runs on port 5001 instead.
- The Vercel deployment uses environment variables set via `vercel env add`.

---

_Last updated: March 2026_
