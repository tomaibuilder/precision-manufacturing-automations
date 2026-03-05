# HR Onboarding Automation - Runbook

## Overview

**What it does:** Automates the new hire onboarding process. When HR adds a new employee, the system generates 5 onboarding documents (offer letter, IT request, facilities request, manager prep checklist, welcome email) and tracks progress through a web dashboard.

**Why it exists:** Rachel in HR was spending 2-3 hours per new hire writing the same emails and documents from scratch. This automation generates everything in seconds and provides a visual dashboard to track onboarding progress.

**Who uses it:** HR team (Rachel Kim's department)

**Dashboard URL:** https://webapp-nine-rho-64.vercel.app

**GitHub:** https://github.com/tomaibuilder/hr-onboarding-automation

**Impact:** Saves ~8-10 hours per new hire. Ensures consistency across all onboarding documents. Nothing gets forgotten.

---

## Setup & Prerequisites

### For Dashboard Users (No Setup Needed)

Go to: **https://webapp-nine-rho-64.vercel.app**

### For CLI Users

```bash
cd /path/to/hr-onboarding
python3 -m venv venv
source venv/bin/activate
pip install requests python-dotenv
```

### .env File

```
AIRTABLE_TOKEN=your_personal_access_token
AIRTABLE_BASE_ID=your_base_id
```

### Airtable Table: "Onboarding"

| Field | Type | Options |
|-------|------|---------|
| Employee Name | Single line text | |
| Position | Single line text | |
| Department | Single select | Engineering, Sales, Finance, Operations, Marketing, HR, Customer Service |
| Manager | Single line text | |
| Start Date | Date | |
| Salary | Currency | |
| Email | Single line text | Auto-generated: first.last@precisionmfg.com |
| Status | Single select | Offer Pending, Offer Sent, Offer Signed, IT Setup, Onboarding, Complete |
| Offer Letter Generated | Checkbox | |
| IT Request Sent | Checkbox | |
| Facilities Request Sent | Checkbox | |
| Manager Notified | Checkbox | |
| First Day Agenda Sent | Checkbox | |
| Notes | Long text | |

---

## How to Use It

### Option A: Web Dashboard (Recommended)

1. **Open:** https://webapp-nine-rho-64.vercel.app
2. **Add a new hire:** Click "+ New Hire", fill in the form
3. **Generate documents:** Click "Generate Documents" on the employee's card
4. **View documents:** Click "View Documents" to see all 5 generated documents
5. **Track progress:** Use "Advance Status" to move through the workflow:
   - Offer Pending -> Offer Sent -> Offer Signed -> IT Setup -> Onboarding -> Complete

### Option B: Command Line

**Process all pending hires:**
```bash
cd /path/to/hr-onboarding
source venv/bin/activate
python onboarding_automation.py
```

**Add a new hire interactively:**
```bash
python onboarding_automation.py --add
```

**View dashboard in terminal:**
```bash
python onboarding_automation.py --status
```

**Generate docs for a specific record:**
```bash
python onboarding_automation.py --generate RECORD_ID
```

### What Gets Generated

For each new hire, 5 documents are created:

1. **Offer Letter** - Formal job offer with position, salary, start date
2. **IT Setup Request** - Email to IT with equipment needs (laptop type based on department)
3. **Facilities Request** - Desk setup, badge, parking pass request
4. **Manager Prep Checklist** - Onboarding checklist for the hiring manager
5. **Welcome Email** - First-day schedule, what to bring, who to ask for

### Smart Defaults

- **Email:** Auto-generated as first.last@precisionmfg.com
- **Laptop:** MacBook Pro for Engineering/Marketing/HR, Dell Latitude for others
- **Offer deadline:** 7 days from generation date

---

## What Could Go Wrong

### Dashboard shows "Loading..." forever
**Fix:** Check your internet connection. Try refreshing. If the API is down, check Vercel deployment status.

### "Failed to load records"
**Cause:** Airtable API issue
**Fix:** Check that the Airtable token hasn't expired. Check https://status.airtable.com

### Documents show "TBD" for fields
**Cause:** Missing data in the employee record
**Fix:** Edit the record in Airtable (or the dashboard) to fill in missing fields, then regenerate documents.

### Wrong laptop type in IT request
**Cause:** Department might not match expected values
**Fix:** Only Engineering, Marketing, and HR get MacBooks. All others get Dell. Update department in Airtable if wrong.

### CLI: "ModuleNotFoundError: No module named 'requests'"
**Fix:** Activate the virtual environment:
```bash
source venv/bin/activate
pip install requests python-dotenv
```

---

## Monitoring & Verification

### Check Dashboard

Visit https://webapp-nine-rho-64.vercel.app and verify:
- Stats bar shows correct counts
- All employee cards load with proper status badges
- Progress bars reflect checklist completion

### Check Airtable

Open the Onboarding table and verify:
- Checkboxes are marked after document generation
- Status updates correctly through the workflow
- Notes field shows generation timestamp

### Check CLI Output

When processing:
```
Processing: James Rodriguez (Manufacturing Engineer)
  Generated: Offer Letter
  Generated: IT Setup Request
  Generated: Facilities Request
  Generated: Manager Prep Checklist
  Generated: Welcome Email
  Updated Airtable: Status -> Offer Sent
  Documents saved to: output/james-rodriguez/
```

---

## Maintenance

### Monthly

- Review document templates for accuracy (address changes, policy updates)
- Check that department list in Airtable matches dashboard dropdown
- Test document generation with a dummy record

### When Templates Need Updates

Templates are stored in two places:
1. **CLI version:** `hr-onboarding/templates/*.txt` (file-based)
2. **Vercel version:** `hr-onboarding/webapp/api/index.py` (embedded in code)

Update BOTH when changing templates, then redeploy:
```bash
cd hr-onboarding/webapp
vercel --prod
```

### Redeploying the Dashboard

```bash
cd /path/to/hr-onboarding/webapp
vercel --prod
```

---

## Emergency Procedures

### Dashboard Is Down

Use the CLI version as fallback:
```bash
python onboarding_automation.py --add    # Add new hire
python onboarding_automation.py          # Process pending
python onboarding_automation.py --status # View status
```

Generated documents are saved locally in `output/[employee-name]/`.

### Manual Fallback

If everything is broken, copy templates from `templates/` folder and fill in employee details by hand in a text editor.

### Contact

- **Maintainer:** [AI Operations Lead]
- **HR Lead:** Rachel Kim
- **Escalation:** [Manager name]
