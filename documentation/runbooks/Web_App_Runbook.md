# Invoice Upload Web App - Runbook

## Overview

**What it does:** A web-based interface where Finance staff can upload invoice PDFs one at a time, review extracted data, make corrections, and save to Airtable. Deployed on Vercel, accessible from any browser.

**Why it exists:** The batch processor works great for bulk processing, but Finance needed a way to handle individual invoices throughout the day without touching the command line.

**Who uses it:** Finance team members (non-technical users)

**Live URL:** https://invoice-webapp-five.vercel.app

**Impact:** Any Finance team member can process an invoice in 30 seconds without technical knowledge.

---

## Setup & Prerequisites

### For Users (No Setup Needed)

Just go to: **https://invoice-webapp-five.vercel.app**

Works in any modern browser (Chrome, Firefox, Safari, Edge).

### For Maintainers

**Local Development:**

```bash
cd /path/to/invoice-webapp
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors pdfplumber requests python-dotenv
python api/index.py
```

Local server runs at: http://localhost:5000

**Deployment Platform:** Vercel (https://vercel.com)

**Environment Variables (Vercel Dashboard):**

| Variable | Value |
|----------|-------|
| AIRTABLE_TOKEN | Your Airtable personal access token |
| AIRTABLE_BASE_ID | Your Airtable base ID |

---

## How to Use It (For Finance Staff)

### Step 1: Open the Web App

Go to https://invoice-webapp-five.vercel.app in your browser.

### Step 2: Upload an Invoice

- Click the upload area (or drag and drop a PDF onto it)
- Only PDF files are accepted
- Wait 2-3 seconds for processing

### Step 3: Review Extracted Data

The app shows extracted fields:
- Vendor name
- Invoice number
- Dates (invoice date, due date)
- Amounts (subtotal, tax, total)
- Confidence score (green = high accuracy, yellow = review needed)

### Step 4: Make Corrections

Click any field to edit it if the extraction wasn't perfect.

### Step 5: Save to Airtable

Click "Save to Airtable" to create the record.
A green checkmark confirms it was saved.

### What Success Looks Like

- Green confidence badge (0.85+)
- All fields populated correctly
- "Saved to Airtable" confirmation message
- Record appears in Airtable Invoices table

---

## What Could Go Wrong

### "Failed to process file"
**Cause:** PDF might be scanned/image-based or corrupted
**Fix:** Try a different PDF. If the same file works in the batch processor, report the issue to the maintainer.

### "Duplicate invoice detected"
**Cause:** This invoice number already exists in Airtable
**Fix:** Check Airtable for the existing record. If it's a legitimate re-upload, delete the old record first.

### Page is blank or won't load
**Fix:** Try refreshing the browser. If still broken, check https://vercel.com/dashboard for deployment status.

### "Save failed"
**Cause:** Airtable API issue (token expired, rate limit, or service outage)
**Fix:** Wait 30 seconds and try again. If persistent, check that Vercel environment variables are correct.

### Low confidence score (yellow/red)
**Fix:** Review all extracted fields carefully. Edit any incorrect values before saving.

---

## Monitoring & Verification

### Check Deployment Status

```bash
cd /path/to/invoice-webapp
vercel ls
```

Or visit: https://vercel.com/dashboard

### Check Vercel Function Logs

```bash
vercel logs [deployment-url]
```

Or view in Vercel Dashboard > Project > Functions tab

### Verify API Is Working

```bash
curl https://invoice-webapp-five.vercel.app/api/process -X POST
# Should return: {"error": "No file provided"}
```

If this returns an error page, the deployment is broken.

---

## Maintenance

### Redeploying After Code Changes

```bash
cd /path/to/invoice-webapp
vercel --prod
```

### Updating Environment Variables

```bash
# Remove old value
vercel env rm AIRTABLE_TOKEN production

# Add new value (use printf to avoid trailing newline)
printf '%s' 'new_token_value' | vercel env add AIRTABLE_TOKEN production

# Redeploy
vercel --prod
```

### Monthly

- Test upload with a sample invoice
- Check Vercel usage (free tier: 100GB bandwidth, 100 hours serverless)
- Review error logs in Vercel dashboard

### Quarterly

- Update Python packages in `requirements.txt`
- Test locally before redeploying
- Check Vercel for platform updates

---

## Emergency Procedures

### Web App Is Down

1. Check Vercel status: https://www.vercel-status.com
2. Try redeploying: `vercel --prod`
3. If Vercel is down, use the batch processor as fallback

### Airtable Token Expired

1. Generate new token at https://airtable.com/create/tokens
2. Update in Vercel: see "Updating Environment Variables" above
3. Redeploy

### Manual Fallback

If the web app is broken, invoices can still be processed:
1. Download PDFs locally
2. Place in `invoice-automation/invoices/` folder
3. Run: `python scripts/process_invoices.py`

### Contact

- **Maintainer:** [AI Operations Lead]
- **Vercel Account:** [Account owner]
- **Escalation:** [Manager name]
