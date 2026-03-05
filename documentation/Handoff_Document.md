# Precision Manufacturing Automations - Handoff Document

*Everything you need to take over and maintain these systems.*

---

## What You're Receiving

### 4 Working Automations

| # | Automation | What It Does | Users |
|---|-----------|-------------|-------|
| 1 | **Invoice Processor** | Extracts data from PDF invoices, saves to Airtable | Finance |
| 2 | **Drive Automation** | Watches Google Drive for new invoices, auto-processes | Finance |
| 3 | **Invoice Web App** | Web upload interface for individual invoices | Finance |
| 4 | **HR Onboarding Dashboard** | Generates onboarding docs, tracks new hire progress | HR |

### Complete Documentation

| Document | Location | Audience |
|----------|----------|----------|
| 4 Runbooks | `documentation/runbooks/` | Operators / Maintainers |
| 2 Quick Start Guides | `documentation/quick-starts/` | End Users |
| FAQ | `documentation/training/FAQ.md` | Everyone |
| Maintenance Guide | `documentation/training/Maintenance_Guide.md` | Maintainers |
| CLAUDE.md Playbook | Root `CLAUDE.md` | Developers / AI Operators |
| This Handoff Document | `documentation/Handoff_Document.md` | New Maintainer |

### Code Repositories

| Repo | URL | Contains |
|------|-----|----------|
| Precision Manufacturing Automations | https://github.com/tomaibuilder/precision-manufacturing-automations | Invoice processor, Drive watcher, Web app |
| HR Onboarding Automation | https://github.com/tomaibuilder/hr-onboarding-automation | Onboarding CLI + templates |

### Deployed Web Apps

| App | URL | Platform |
|-----|-----|----------|
| Invoice Upload | https://invoice-webapp-five.vercel.app | Vercel |
| HR Onboarding Dashboard | https://webapp-nine-rho-64.vercel.app | Vercel |

### Data

| System | Platform | What's There |
|--------|----------|-------------|
| Invoices | Airtable (base: appAnYfILXyoOzSTg) | All processed invoice records |
| Onboarding | Airtable (base: appAnYfILXyoOzSTg) | Employee onboarding records |
| Invoice PDFs | Google Drive | Processed and unprocessed invoices |

---

## Quick Start for New Maintainer

### Week 1: Get Access

- [ ] Clone GitHub repositories
- [ ] Get Airtable personal access token (ask current admin)
- [ ] Get Google Drive API credentials (ask IT)
- [ ] Get Vercel account access (ask current owner)
- [ ] Set up local `.env` files with credentials
- [ ] Install Python 3.10+ and create virtual environments

### Week 1: Verify Everything Works

```bash
# 1. Test invoice processor
cd /path/to/invoice-automation
source venv/bin/activate
cp test_data/invoice-001-acme-corp.pdf invoices/
python scripts/process_invoices.py
# Verify: record appears in Airtable, PDF moves to processed/

# 2. Test Drive watcher
python drive-watcher/drive_invoice_watcher.py --once
# Verify: checks Drive folder (may find nothing, that's OK)

# 3. Test web apps
curl https://invoice-webapp-five.vercel.app/  # Should return HTML
curl https://webapp-nine-rho-64.vercel.app/api/records  # Should return JSON

# 4. Test HR automation
cd /path/to/hr-onboarding
source venv/bin/activate
python onboarding_automation.py --status
# Verify: shows current onboarding records
```

### Week 2: Understand the Systems

- [ ] Read all 4 runbooks in `documentation/runbooks/`
- [ ] Read the CLAUDE.md playbook (architecture decisions, known limitations)
- [ ] Read the FAQ
- [ ] Process a real invoice through the web app
- [ ] Add a test employee to the HR dashboard and generate documents

### Month 1: Build Confidence

- [ ] Run each automation independently at least once
- [ ] Troubleshoot a minor issue (check logs, fix, verify)
- [ ] Update the documentation for something you learned
- [ ] Meet with Finance and HR stakeholders to introduce yourself
- [ ] Follow the Monthly tasks in the Maintenance Guide

---

## Key Architecture Decisions

These explain WHY things were built this way:

| Decision | Why |
|----------|-----|
| **pdfplumber (not OCR)** | Vendor invoices are digital PDFs. pdfplumber is fast, free, and accurate for text-based PDFs. OCR would be slower and less accurate. |
| **Regex extraction (not AI)** | Regex is deterministic, fast, and free. AI extraction would cost per-invoice and introduce variability. Regex covers 95% of invoice formats. |
| **Airtable (not a database)** | Finance already knows spreadsheets. Airtable gives them a familiar interface with API access for automation. |
| **Flask (not Django/FastAPI)** | Simplicity. These are small apps with a few endpoints. Flask is the lightest option. |
| **Vercel (not AWS/GCP)** | Free tier is generous, deployment is one command, no infrastructure management. |
| **Templates as strings (Vercel)** | Vercel serverless functions can't access parent directories. Templates are embedded in the code for the deployed version. |

---

## Known Issues & Workarounds

| Issue | Workaround | Priority |
|-------|-----------|----------|
| Tech Parts Inc invoices sometimes extract HTML artifacts | Manual review needed for this vendor | Low |
| Regex patterns tuned for 5 test vendors | New vendor formats may need pattern updates in `process_invoices.py` | Medium |
| Web apps have no authentication | Currently OK for internal use. Add auth if exposed externally. | Medium |
| HR templates stored in two places (files + embedded) | Update BOTH when changing templates | Low |
| Google OAuth token expires periodically | Delete `token.json` and re-authenticate | Low |

---

## Key Contacts

| Role | Name | Contact | Notes |
|------|------|---------|-------|
| Finance Lead | Sarah | [email] | Primary user of invoice tools |
| HR Manager | Rachel Kim | [email] | Primary user of onboarding dashboard |
| IT Admin | [Name] | [email] | Google Drive access, network issues |
| Previous Maintainer | [Your name] | [email] | Built the systems, available for questions |

---

## Future Enhancement Ideas

These are improvements that were identified but not yet built:

1. **Add authentication to web apps** - Important if URLs are shared outside the company
2. **Email integration** - Auto-send generated HR documents instead of copy/paste
3. **Purchase order processing** - Similar to invoice processor, for POs
4. **Employee offboarding automation** - Mirror of the onboarding system
5. **Vendor onboarding** - Auto-setup for new suppliers
6. **Dashboard analytics** - Charts showing processing volumes, error rates over time
7. **Slack notifications** - Alert Finance when invoices are processed, alert HR when docs are generated
8. **OCR fallback** - For scanned/image-based PDFs that pdfplumber can't handle

---

## One Last Thing

These automations save the company 100+ hours per month. That impact only continues if someone maintains them. Follow the Maintenance Guide, keep the documentation updated, and don't let the automations rot from neglect.

If you get stuck, read the CLAUDE.md playbook. It was written specifically to help the next person understand and extend these systems.

Good luck. You've got this.
