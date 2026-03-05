#!/usr/bin/env python3
"""
Invoice PDF Processor
Extracts invoice data from PDFs and uploads to Airtable.

Usage:
    source venv/bin/activate
    python3 scripts/process_invoices.py

Built for: Precision Manufacturing - Finance Department
"""

import os
import sys
import re
import json
import shutil
import logging
import time
from datetime import datetime
from typing import Dict, Optional

import pdfplumber
import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Resolve paths relative to the project root (one level up from scripts/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'Invoices')

INVOICES_DIR = os.path.join(PROJECT_ROOT, 'invoices')
PROCESSED_DIR = os.path.join(PROJECT_ROOT, 'processed')
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')

CONFIDENCE_THRESHOLD = 0.90

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

os.makedirs(LOGS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'processing.log')),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helper: strip HTML-like tags from pdfplumber output
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Remove HTML-like tags that pdfplumber sometimes leaves in extracted text."""
    # Remove tags like <b>, </b>, <font ...>, </font>, <br/>, etc.
    cleaned = re.sub(r'<[^>]+>', ' ', text)
    # Collapse multiple spaces
    cleaned = re.sub(r'  +', ' ', cleaned)
    return cleaned.strip()

# ---------------------------------------------------------------------------
# Step 6: PDF Reader
# ---------------------------------------------------------------------------

def read_pdf(filepath: str) -> Optional[str]:
    """
    Extract all text from a PDF file.

    Returns:
        Combined text from all pages, or None on failure.
    """
    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        return None

    if not filepath.lower().endswith('.pdf'):
        logger.warning(f"Skipping non-PDF file: {os.path.basename(filepath)}")
        return None

    try:
        logger.info(f"Reading PDF: {os.path.basename(filepath)}")
        with pdfplumber.open(filepath) as pdf:
            pages_text = []
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
                    logger.info(f"  Page {page_num}: {len(page_text)} chars extracted")
                else:
                    logger.warning(f"  Page {page_num}: no text extracted")

            if not pages_text:
                logger.error(f"No text could be extracted from {os.path.basename(filepath)}")
                return None

            raw_text = "\n".join(pages_text)
            return clean_text(raw_text)

    except Exception as e:
        logger.error(f"Cannot read {os.path.basename(filepath)}: {e}")
        return None

# ---------------------------------------------------------------------------
# Step 7: Data Extraction
# ---------------------------------------------------------------------------

def extract_invoice_number(text: str) -> Optional[str]:
    """Extract invoice number from text."""
    patterns = [
        r'Invoice\s*#\s*:?\s*([A-Z0-9][\w-]+)',
        r'Invoice\s+Number\s*:?\s*([A-Z0-9][\w-]+)',
        r'Invoice\s*:?\s*(INV[-\s]?\d[\w-]*)',
        r'Invoice\s*:?\s*([A-Z]{2,3}-\d[\w-]*)',
        # Catch standalone invoice number patterns (e.g. TP-2024-0891, WS-789456)
        r'\b([A-Z]{2,3}-\d{4}-\d{3,5})\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            logger.info(f"  Invoice Number: {value}")
            return value

    logger.warning("  Could not find invoice number")
    return None


def extract_vendor_name(text: str) -> Optional[str]:
    """Extract vendor name – usually in the first few lines."""
    lines = text.split('\n')
    company_suffixes = [
        r'Corp\.?', r'Inc\.?', r'LLC', r'Ltd\.?', r'Limited',
        r'Corporation', r'Company', r'Co\.', r'Solutions',
        r'Supplies', r'Direct', r'Depot',
    ]
    suffix_pattern = '|'.join(company_suffixes)

    for line in lines[:10]:
        line = line.strip()
        if not line or len(line) < 3:
            continue
        if re.search(rf'\b({suffix_pattern})\b', line, re.IGNORECASE):
            # Exclude lines that are clearly addresses or phone numbers
            if re.match(r'^\d', line) or 'phone' in line.lower() or 'tel:' in line.lower():
                continue
            logger.info(f"  Vendor: {line}")
            return line

    logger.warning("  Could not find vendor name")
    return None


def extract_date(text: str, label: str) -> Optional[str]:
    """
    Extract a date associated with a label (e.g. 'Invoice Date', 'Due Date').
    Returns date in YYYY-MM-DD format.
    """
    # Build pattern: label, optional colon/space, then a date
    pattern = rf'{label}\s*:?\s*(\d{{1,2}}[/\-]\d{{1,2}}[/\-]\d{{4}}|\d{{4}}[/\-]\d{{1,2}}[/\-]\d{{1,2}})'
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return normalize_date(match.group(1))

    # Fallback: try just "Date:" if label is "Invoice Date" and first attempt failed
    if label.lower() == 'invoice date':
        fallback = re.search(r'(?<!\bDue\s)Date\s*:?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})', text, re.IGNORECASE)
        if fallback:
            return normalize_date(fallback.group(1))

    # Last resort: find ALL dates in the text and pick the first (invoice date) or second (due date)
    all_dates = re.findall(r'(\d{2}/\d{2}/\d{4})', text)
    if all_dates:
        if label.lower() == 'invoice date' and len(all_dates) >= 1:
            logger.info(f"  {label} (fallback - positional): {all_dates[0]}")
            return normalize_date(all_dates[0])
        if label.lower() == 'due date' and len(all_dates) >= 2:
            logger.info(f"  {label} (fallback - positional): {all_dates[1]}")
            return normalize_date(all_dates[1])

    logger.warning(f"  Could not find {label}")
    return None


def normalize_date(date_str: str) -> Optional[str]:
    """Convert various date formats to YYYY-MM-DD."""
    date_str = date_str.strip()
    formats = ['%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%d-%m-%Y']
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            result = dt.strftime('%Y-%m-%d')
            logger.info(f"  Date parsed: {date_str} -> {result}")
            return result
        except ValueError:
            continue
    logger.warning(f"  Could not normalize date: {date_str}")
    return date_str


def extract_amount(text: str, label: str = "Total") -> Optional[float]:
    """Extract a monetary amount associated with a label."""
    if label == "Total":
        # For "Total", match "Total Due", "TOTAL DUE", "AMOUNT DUE", "TOTAL:" but NOT "Subtotal"
        patterns = [
            r'(?:TOTAL\s*DUE|Total\s*Due|AMOUNT\s*DUE|Amount\s*Due)\s*:?\s*\$?\s*([\d,]+\.\d{2})',
            r'(?<![Ss]ub)TOTAL\s*:\s*\$?\s*([\d,]+\.\d{2})',
            r'(?<![Ss]ub)Total\s*:\s*\$?\s*([\d,]+\.\d{2})',
        ]
    elif label == "Tax":
        # Tax might appear as "Tax (8%):", "Sales Tax (8%):", or just "Tax:"
        patterns = [
            r'(?:Sales\s+)?Tax\s*(?:\([^)]*\))?\s*:?\s*\$?\s*([\d,]+\.\d{2})',
        ]
    else:
        patterns = [
            rf'{label}\s*:?\s*\$?\s*([\d,]+\.\d{{2}})',
        ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                amount = float(amount_str)
                logger.info(f"  {label}: ${amount:.2f}")
                return amount
            except ValueError:
                continue

    # Last resort for Total: if we have subtotal and tax, calculate it
    if label == "Total":
        subtotal_match = re.search(r'Subtotal\s*:?\s*\$?\s*([\d,]+\.\d{2})', text, re.IGNORECASE)
        tax_match = re.search(r'(?:Sales\s+)?Tax\s*(?:\([^)]*\))?\s*:?\s*\$?\s*([\d,]+\.\d{2})', text, re.IGNORECASE)
        if subtotal_match and tax_match:
            subtotal = float(subtotal_match.group(1).replace(',', ''))
            tax = float(tax_match.group(1).replace(',', ''))
            total = round(subtotal + tax, 2)
            logger.info(f"  {label}: ${total:.2f} (calculated from subtotal + tax)")
            return total

    logger.warning(f"  Could not find {label} amount")
    return None


def extract_invoice_data(text: str) -> Dict:
    """Extract all required fields from invoice text."""
    logger.info("Extracting invoice data...")

    data = {
        'invoice_number': extract_invoice_number(text),
        'vendor_name': extract_vendor_name(text),
        'invoice_date': extract_date(text, 'Invoice Date'),
        'due_date': extract_date(text, 'Due Date'),
        'total_amount': extract_amount(text, 'Total'),
        'subtotal': extract_amount(text, 'Subtotal'),
        'tax': extract_amount(text, 'Tax'),
    }

    data['confidence_score'] = calculate_confidence(data)
    return data


def calculate_confidence(data: Dict) -> float:
    """
    Confidence = proportion of required fields successfully extracted.
    Each of the 5 required fields contributes 0.20.
    """
    required = ['invoice_number', 'vendor_name', 'invoice_date', 'due_date', 'total_amount']
    found = sum(1 for f in required if data.get(f) is not None)
    score = round(found / len(required), 2)
    logger.info(f"  Confidence: {score:.2f} ({found}/{len(required)} fields)")
    return score

# ---------------------------------------------------------------------------
# Step 8: Data Validation
# ---------------------------------------------------------------------------

def validate_invoice(data: Dict) -> tuple:
    """
    Validate extracted data.
    Returns (is_valid, list_of_errors).
    """
    errors = []

    # Required fields
    for field in ['invoice_number', 'vendor_name', 'invoice_date', 'due_date', 'total_amount']:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")

    # Date format
    for field in ['invoice_date', 'due_date']:
        val = data.get(field)
        if val and not _is_valid_date(val):
            errors.append(f"Invalid date format for {field}: {val}")

    # Due date >= invoice date
    if data.get('invoice_date') and data.get('due_date'):
        try:
            inv = datetime.strptime(data['invoice_date'], '%Y-%m-%d')
            due = datetime.strptime(data['due_date'], '%Y-%m-%d')
            if due < inv:
                errors.append(f"Due date ({data['due_date']}) is before invoice date ({data['invoice_date']})")
        except ValueError:
            pass

    # Amount > 0
    if data.get('total_amount') is not None and data['total_amount'] <= 0:
        errors.append(f"Total amount must be positive: {data['total_amount']}")

    # Subtotal + tax = total (within tolerance)
    if data.get('subtotal') and data.get('tax') and data.get('total_amount'):
        expected = data['subtotal'] + data['tax']
        if abs(expected - data['total_amount']) > 0.10:
            errors.append(
                f"Amount mismatch: subtotal({data['subtotal']}) + tax({data['tax']}) "
                f"= {expected:.2f}, but total is {data['total_amount']}"
            )

    if errors:
        logger.warning(f"  Validation issues: {errors}")
    else:
        logger.info("  Validation passed")

    return len(errors) == 0, errors


def _is_valid_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# ---------------------------------------------------------------------------
# Step 9: Airtable Upload
# ---------------------------------------------------------------------------

def check_duplicate(invoice_number: str) -> bool:
    """Check if an invoice number already exists in Airtable."""
    if not AIRTABLE_TOKEN or not AIRTABLE_BASE_ID:
        return False

    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    params = {"filterByFormula": f"{{Invoice Number}} = '{invoice_number}'", "maxRecords": 1}

    try:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code == 200:
            records = resp.json().get('records', [])
            if records:
                logger.info(f"  Duplicate found: {invoice_number} already in Airtable")
                return True
        elif resp.status_code in (401, 403):
            logger.critical("Airtable authentication failed. Check your API token.")
            sys.exit(1)
        else:
            logger.error(f"  Airtable lookup failed: {resp.status_code} {resp.text}")
    except Exception as e:
        logger.error(f"  Error checking duplicate: {e}")

    return False


def upload_to_airtable(data: Dict) -> bool:
    """Create a record in Airtable with extracted invoice data."""
    if not AIRTABLE_TOKEN or not AIRTABLE_BASE_ID:
        logger.error("Airtable credentials not configured in .env")
        return False

    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }

    status = "Received" if data.get('confidence_score', 0) >= CONFIDENCE_THRESHOLD else "Under Review"

    fields = {
        "Invoice Number": data.get('invoice_number'),
        "Vendor": data.get('vendor_name'),
        "Invoice Date": data.get('invoice_date'),
        "Due Date": data.get('due_date'),
        "Amount": data.get('total_amount'),
        "Status": status,
        "Confidence": data.get('confidence_score'),
        "Notes": f"Auto-extracted | Confidence: {data.get('confidence_score', 0):.2f}",
    }

    # Strip None values – Airtable rejects null for some field types
    fields = {k: v for k, v in fields.items() if v is not None}

    try:
        logger.info(f"  Uploading to Airtable ({status})...")
        resp = requests.post(url, headers=headers, json={"fields": fields})

        if resp.status_code == 200:
            record_id = resp.json().get('id', 'unknown')
            logger.info(f"  Record created: {record_id}")
            return True

        # Retry once on server error / rate limit
        if resp.status_code in (429, 500, 502, 503):
            logger.warning(f"  Airtable returned {resp.status_code}, retrying in 5s...")
            time.sleep(5)
            resp = requests.post(url, headers=headers, json={"fields": fields})
            if resp.status_code == 200:
                record_id = resp.json().get('id', 'unknown')
                logger.info(f"  Record created on retry: {record_id}")
                return True

        if resp.status_code in (401, 403):
            logger.critical("Airtable authentication failed. Check your API token.")
            sys.exit(1)

        logger.error(f"  Airtable API error: {resp.status_code} {resp.text}")
        return False

    except Exception as e:
        logger.error(f"  Exception uploading to Airtable: {e}")
        return False

# ---------------------------------------------------------------------------
# Step 10: Main Processing Pipeline
# ---------------------------------------------------------------------------

def process_invoice(filepath: str) -> str:
    """
    Process a single invoice PDF end-to-end.

    Returns one of: 'success', 'flagged', 'skipped', 'failed'
    """
    filename = os.path.basename(filepath)

    # Read PDF
    text = read_pdf(filepath)
    if text is None:
        return 'failed'

    # Extract data
    data = extract_invoice_data(text)

    # Check for duplicate
    inv_num = data.get('invoice_number')
    if inv_num and check_duplicate(inv_num):
        logger.info(f"  Skipped {inv_num} - already exists in Airtable")
        return 'skipped'

    # Validate
    is_valid, errors = validate_invoice(data)

    # Determine status
    if data['confidence_score'] < CONFIDENCE_THRESHOLD:
        logger.warning(f"  Low confidence ({data['confidence_score']:.2f}) - flagging for review")

    # Upload to Airtable (even low-confidence records, marked "Under Review")
    if not upload_to_airtable(data):
        return 'failed'

    # Move processed file
    dest = os.path.join(PROCESSED_DIR, filename)
    try:
        shutil.move(filepath, dest)
        logger.info(f"  Moved to processed/: {filename}")
    except Exception as e:
        logger.error(f"  Could not move file: {e}")

    if data['confidence_score'] < CONFIDENCE_THRESHOLD or not is_valid:
        return 'flagged'
    return 'success'


def process_all_invoices():
    """Scan invoices/ folder and process all PDFs."""
    logger.info("=" * 60)
    logger.info("INVOICE PROCESSOR - Starting batch run")
    logger.info("=" * 60)

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # Gather PDF files
    files = sorted([
        os.path.join(INVOICES_DIR, f)
        for f in os.listdir(INVOICES_DIR)
        if os.path.isfile(os.path.join(INVOICES_DIR, f))
    ])

    if not files:
        logger.info("No files found in invoices/ folder. Nothing to process.")
        return

    logger.info(f"Found {len(files)} file(s) in invoices/")

    counts = {'success': 0, 'flagged': 0, 'skipped': 0, 'failed': 0}

    for filepath in files:
        filename = os.path.basename(filepath)
        logger.info(f"\n--- Processing: {filename} ---")

        if not filename.lower().endswith('.pdf'):
            logger.warning(f"Skipping non-PDF file: {filename}")
            counts['failed'] += 1
            continue

        result = process_invoice(filepath)
        counts[result] += 1

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("BATCH SUMMARY")
    logger.info("=" * 60)
    logger.info(f"  Successful : {counts['success']}")
    logger.info(f"  Flagged    : {counts['flagged']}")
    logger.info(f"  Skipped    : {counts['skipped']}")
    logger.info(f"  Failed     : {counts['failed']}")
    logger.info(f"  Total      : {sum(counts.values())}")
    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    process_all_invoices()
