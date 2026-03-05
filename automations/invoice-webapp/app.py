#!/usr/bin/env python3
"""
Invoice Upload Web App - Flask Backend
Accepts PDF uploads, extracts invoice data, saves to Airtable.
"""

import os
import sys
import tempfile
import logging

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Add scripts/ to path so we can import the invoice processor
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'scripts'))

load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

import requests as http_requests
from process_invoices import (
    read_pdf, extract_invoice_data, validate_invoice, check_duplicate
)

AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'Invoices')

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/process', methods=['POST'])
def process_invoice():
    """Accept PDF upload, extract invoice data, return JSON."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are accepted'}), 400

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        # Extract text
        text = read_pdf(tmp_path)
        if text is None:
            return jsonify({'error': 'Could not extract text from PDF'}), 422

        # Extract structured data
        data = extract_invoice_data(text)

        # Validate
        is_valid, errors = validate_invoice(data)

        # Check for duplicates
        is_duplicate = False
        if data.get('invoice_number'):
            is_duplicate = check_duplicate(data['invoice_number'])

        return jsonify({
            'success': True,
            'data': {
                'invoice_number': data.get('invoice_number'),
                'vendor_name': data.get('vendor_name'),
                'invoice_date': data.get('invoice_date'),
                'due_date': data.get('due_date'),
                'total_amount': data.get('total_amount'),
                'subtotal': data.get('subtotal'),
                'tax': data.get('tax'),
                'confidence_score': data.get('confidence_score'),
            },
            'validation': {
                'is_valid': is_valid,
                'errors': errors,
            },
            'is_duplicate': is_duplicate,
        })

    except Exception as e:
        logger.error(f"Processing error: {e}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

    finally:
        os.unlink(tmp_path)


@app.route('/api/save', methods=['POST'])
def save_to_airtable():
    """Save invoice data to Airtable."""
    if not AIRTABLE_TOKEN or not AIRTABLE_BASE_ID:
        return jsonify({'error': 'Airtable not configured'}), 500

    body = request.get_json()
    if not body:
        return jsonify({'error': 'No data provided'}), 400

    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }

    confidence = body.get('confidence_score', 0)
    status = "Received" if confidence >= 0.90 else "Under Review"

    fields = {
        "Invoice Number": body.get('invoice_number'),
        "Vendor": body.get('vendor_name'),
        "Invoice Date": body.get('invoice_date'),
        "Due Date": body.get('due_date'),
        "Amount": body.get('total_amount'),
        "Status": status,
        "Confidence": confidence,
        "Notes": f"Uploaded via web app | Confidence: {confidence:.2f}",
    }
    fields = {k: v for k, v in fields.items() if v is not None}

    try:
        resp = http_requests.post(url, headers=headers, json={"fields": fields})
        if resp.status_code == 200:
            record_id = resp.json().get('id', 'unknown')
            return jsonify({'success': True, 'record_id': record_id})
        else:
            return jsonify({'error': f'Airtable error: {resp.status_code}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True, port=5001)
