# Automation Maintenance Guide

*Keeping your automations healthy and running.*

---

## Daily Checks

**Time: 2 minutes**

- [ ] Verify the Drive watcher is running (if using continuous mode):
  ```bash
  ps aux | grep drive_invoice_watcher
  ```
- [ ] Glance at Airtable Invoices table - any records from today? If invoices were uploaded but no records appeared, investigate.

---

## Weekly Tasks

**Time: 15 minutes | Suggested: Monday morning**

### Check Logs for Errors

```bash
# Invoice processor logs
tail -50 /path/to/invoice-automation/logs/processing.log

# Drive watcher logs
tail -50 /path/to/invoice-automation/logs/drive_watcher.log

# HR onboarding logs
tail -50 /path/to/hr-onboarding/logs/onboarding.log
```

Look for:
- Repeated `ERROR` messages (indicates a recurring problem)
- `Rate limit` warnings (too many API calls)
- `Connection` errors (network or API outages)

### Verify Web Apps Are Online

1. Open https://invoice-webapp-five.vercel.app - should show the upload page
2. Open https://webapp-nine-rho-64.vercel.app - should show the HR dashboard with current records

### Check Airtable Data Quality

- Open Invoices table: sort by date, spot-check 2-3 recent entries against actual PDFs
- Open Onboarding table: verify statuses are progressing (no stuck records)

---

## Monthly Tasks

**Time: 30 minutes | Suggested: First Monday of each month**

### Update Python Dependencies

```bash
# Invoice automation
cd /path/to/invoice-automation
source venv/bin/activate
pip install --upgrade pdfplumber requests python-dotenv
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# HR onboarding
cd /path/to/hr-onboarding
source venv/bin/activate
pip install --upgrade requests python-dotenv
```

After updating, test with sample data:
```bash
# Test invoice processor
cd /path/to/invoice-automation
python scripts/process_invoices.py  # with test PDFs in invoices/ folder

# Test HR automation
cd /path/to/hr-onboarding
python onboarding_automation.py --status
```

### Archive Old Logs

```bash
# If log files exceed 1MB, archive them
cd /path/to/invoice-automation/logs
gzip processing.log && mv processing.log.gz "processing-$(date +%Y-%m).log.gz"
touch processing.log

# Same for other log files
```

### Check Vercel Usage

1. Go to https://vercel.com/dashboard
2. Check bandwidth usage (free tier: 100GB/month)
3. Check serverless function execution time (free tier: 100 hours/month)
4. If approaching limits, consider upgrading or optimizing

### Review Processed Files

```bash
# Check how many processed invoices are stored
ls /path/to/invoice-automation/processed/ | wc -l

# Archive old processed files if needed
# (These are copies - originals are in Airtable)
```

### Test Document Generation

Add a test employee to the HR dashboard with dummy data, generate documents, verify they look correct, then delete the test record.

---

## Quarterly Tasks

**Time: 1 hour | Suggested: First week of Jan, Apr, Jul, Oct**

### Full System Test

Run each automation end-to-end:

1. **Invoice Processor:** Process the 5 test invoices in `test_data/`
2. **Drive Watcher:** Upload a test PDF to Google Drive, verify it processes
3. **Web App:** Upload a test PDF via the web interface, verify it saves to Airtable
4. **HR Dashboard:** Add a test hire, generate docs, advance status through all stages

### Review Airtable API Token

- Check if token is still working
- Check token expiration date at https://airtable.com/create/tokens
- If expiring soon, generate a new one and update all `.env` files and Vercel env vars

### Review Google OAuth Token

```bash
ls -la /path/to/invoice-automation/drive-watcher/token.json
```
If the token is old or authentication fails, delete `token.json` and re-authenticate.

### Check Automation Effectiveness

Ask these questions:
- Are the automations still saving time?
- Have any new invoice formats appeared that aren't handled well?
- Are confidence scores consistently high?
- Has the team's workflow changed in ways that affect the automations?

### Update Documentation

- Review runbooks for accuracy
- Update URLs if deployments changed
- Add any new troubleshooting scenarios discovered
- Update FAQ with new questions from the team

---

## Annual Tasks

**Time: 2-3 hours | Suggested: January**

### Rotate API Credentials

1. Generate new Airtable token at https://airtable.com/create/tokens
2. Update all `.env` files locally
3. Update Vercel environment variables:
   ```bash
   cd /path/to/invoice-webapp
   vercel env rm AIRTABLE_TOKEN production
   printf '%s' 'new_token' | vercel env add AIRTABLE_TOKEN production
   vercel --prod

   cd /path/to/hr-onboarding/webapp
   vercel env rm AIRTABLE_TOKEN production
   printf '%s' 'new_token' | vercel env add AIRTABLE_TOKEN production
   vercel --prod
   ```
4. Revoke old token in Airtable
5. Re-authenticate Google OAuth if needed

### Major Version Updates

Check for Python version updates and test compatibility:
```bash
python3 --version
# If a new major version is available, test before upgrading
```

### Architecture Review

- Are there new automation opportunities?
- Should any existing automations be consolidated?
- Are there performance bottlenecks?
- Is the Airtable schema still optimal?

### ROI Report

Calculate and document:
- Total hours saved this year
- Dollar value of time saved
- Number of invoices processed
- Number of employees onboarded
- Error rate and data quality metrics

---

## Emergency Procedures

### An Automation Is Completely Broken

1. **Don't panic.** All automations have manual fallbacks.
2. Check the runbook for the specific automation (in `documentation/runbooks/`)
3. Try the manual fallback process documented in the runbook
4. Check logs for error details
5. If you can't fix it, contact the maintainer

### Airtable Is Down

- Check https://status.airtable.com
- All automations will fail to upload data
- PDFs stay in their input folders and can be reprocessed later
- Wait for Airtable to recover, then run automations again

### Vercel Is Down

- Check https://www.vercel-status.com
- Web apps will be inaccessible
- Use CLI versions of automations as fallback
- Vercel outages are usually resolved within hours

### Data Corruption

- Airtable maintains version history for 2 weeks (free) or 1 year (pro)
- Use Airtable's revision history to restore data
- If records need to be reprocessed, delete them and run the automation again

### Credentials Compromised

1. **Immediately** revoke the compromised token at its source (Airtable, Google, Vercel)
2. Generate new credentials
3. Update all `.env` files and Vercel env vars
4. Check Airtable audit log for unauthorized access
5. Notify IT security

---

## Maintenance Schedule Summary

| Frequency | Tasks | Time |
|-----------|-------|------|
| Daily | Check Drive watcher running, glance at Airtable | 2 min |
| Weekly | Check logs, verify web apps, spot-check data | 15 min |
| Monthly | Update packages, archive logs, check Vercel, test docs | 30 min |
| Quarterly | Full system test, review tokens, update documentation | 1 hr |
| Annual | Rotate credentials, version updates, architecture review, ROI report | 2-3 hrs |
