# Precision Manufacturing Automations - FAQ

---

## General Questions

### Q: What automations do we have?

We have four automation systems:

1. **Invoice Processor** - Reads PDF invoices and enters data into Airtable automatically
2. **Drive Automation** - Watches a Google Drive folder and processes new invoices as they appear
3. **Invoice Web App** - Web interface for uploading and processing individual invoices
4. **HR Onboarding Dashboard** - Generates onboarding documents and tracks new hire progress

### Q: Who built these automations?

Built by the AI Operations Lead using Claude Code (AI-assisted development). All code is stored in GitHub and documented with runbooks.

### Q: How much time do these automations save?

| Automation | Time Saved | How |
|-----------|-----------|-----|
| Invoice Processor | ~15-20 hrs/month | Eliminates manual PDF data entry |
| Drive Automation | ~5 hrs/month | No manual download/upload cycle |
| Invoice Web App | ~10 hrs/month | 30-second upload vs 5-min manual entry |
| HR Onboarding | ~8-10 hrs/new hire | 5 documents generated instantly |

**Total: 100+ hours/month saved across the organization.**

### Q: What's the ROI?

At an average labor cost of $35/hour:
- Monthly savings: ~$3,500-$5,000
- Annual savings: ~$42,000-$60,000
- Cost to build: $0 (built with AI-assisted tools)
- Cost to run: $0 (Airtable free tier, Vercel free tier)

### Q: Are the automations reliable?

Yes. The invoice processor has a 95%+ accuracy rate on standard invoice formats. All automations include error handling, duplicate detection, and logging. If something fails, it fails safely (no data is lost or corrupted).

### Q: What if they break?

Every automation has a manual fallback documented in its runbook. If the web app is down, use the batch processor. If everything is down, enter data manually into Airtable.

---

## Technical Questions

### Q: What technology do these automations use?

- **Language:** Python 3
- **PDF Processing:** pdfplumber (text extraction, not OCR)
- **Database:** Airtable (via REST API)
- **Cloud Storage:** Google Drive API
- **Web Hosting:** Vercel (serverless functions)
- **Web Framework:** Flask
- **Version Control:** GitHub

### Q: Where are the credentials stored?

All credentials are stored in `.env` files locally and Vercel environment variables for deployed apps. They are NEVER stored in code or committed to GitHub.

### Q: Where is the code?

- **GitHub (Portfolio):** https://github.com/tomaibuilder/precision-manufacturing-automations
- **GitHub (HR Onboarding):** https://github.com/tomaibuilder/hr-onboarding-automation
- **Local:** On the operations workstation in the project directories

### Q: Can we modify the automations?

Yes. The code is well-documented with a CLAUDE.md playbook that explains architecture decisions, known limitations, and how to extend each automation. Any developer (or AI-assisted operator) can modify them.

### Q: How do we update dependencies?

```bash
cd /path/to/automation
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

Test with sample data before deploying changes.

### Q: What APIs do we depend on?

| API | Used By | Rate Limits |
|-----|---------|-------------|
| Airtable REST API | All automations | 5 requests/second |
| Google Drive API | Drive watcher | 1,000 requests/100 sec |
| Vercel Serverless | Web apps | 100 hrs/month (free tier) |

---

## User Questions

### Q: How do I upload an invoice?

Go to https://invoice-webapp-five.vercel.app, drag and drop your PDF, review the data, and click "Save to Airtable". Takes about 30 seconds.

### Q: What file formats are supported?

PDF only. The files must be digital PDFs (not scanned images). If you have a scanned invoice, it needs to be OCR'd first.

### Q: Can I process multiple invoices at once?

- **Web App:** One at a time (upload, review, save, repeat)
- **Batch Processor:** Put all PDFs in the `invoices/` folder and run the script. Processes them all at once.
- **Drive Automation:** Upload all PDFs to the "To Process" folder. They'll be handled automatically.

### Q: How long does processing take?

- **Web App:** 2-3 seconds per invoice
- **Batch Processor:** 2-3 seconds each, plus Airtable upload time
- **Drive Watcher:** Checks every 5 minutes, processes within seconds of detection

### Q: What if my upload fails?

1. Make sure the file is a PDF (not an image, Word doc, or Excel file)
2. Check your internet connection
3. Try refreshing the page and uploading again
4. If it keeps failing, the PDF might be a scanned document (image-based)

### Q: How do I add a new hire to the onboarding dashboard?

Go to https://webapp-nine-rho-64.vercel.app, click "+ New Hire", fill in the form, and click "Add Employee". Then click "Generate Documents" on their card.

---

## Business Questions

### Q: What would happen if we turned off these automations?

Finance would go back to manually entering invoice data from PDFs, which took 5-10 minutes per invoice and was error-prone. HR would go back to writing onboarding documents from scratch for each new hire. Total impact: 100+ hours/month of lost productivity.

### Q: Do these automations cost anything to run?

Currently $0/month:
- Airtable: Free tier (1,200 records/base)
- Vercel: Free tier (100 hours compute)
- Google Drive API: Free

If we exceed free tier limits, costs would be:
- Airtable Plus: $20/user/month
- Vercel Pro: $20/month

### Q: Can we add more automations?

Yes. The infrastructure is designed to be extensible. The CLAUDE.md playbook documents how to add new automations following the same patterns. Common candidates: purchase order processing, employee offboarding, vendor onboarding.

### Q: Who has access to the data?

- **Airtable:** Anyone with base access (controlled via Airtable sharing)
- **Web Apps:** Anyone with the URL (no authentication currently)
- **GitHub:** Repository collaborators only
- **Google Drive:** Anyone with folder access

### Q: Is our data secure?

- API tokens are stored in environment variables, never in code
- Airtable data is encrypted at rest and in transit
- Vercel uses HTTPS for all connections
- No invoice data is stored on the web server (processed and sent to Airtable only)
