# Invoice Upload Web App - Quick Start Guide

*For Finance Team Members*

---

## What This Tool Does

Upload a PDF invoice and it automatically reads the vendor name, amounts, dates, and invoice number. You review the data, fix anything that's wrong, and save it to Airtable with one click.

---

## How to Access It

Open this link in your browser:

**https://invoice-webapp-five.vercel.app**

No login required. Works on any computer with internet access.

---

## How to Use It

### Step 1: Upload Your Invoice

- Click the big upload area in the center of the page
- Pick your PDF file
- OR drag the PDF from your desktop and drop it on the page

*You'll see a loading spinner for 2-3 seconds while it reads the invoice.*

### Step 2: Check the Results

The tool shows what it found:

- **Vendor Name** (who sent the invoice)
- **Invoice Number**
- **Invoice Date** and **Due Date**
- **Subtotal, Tax, and Total**

There's also a **confidence score**:
- **Green (85%+):** High accuracy, probably correct
- **Yellow (60-84%):** Medium accuracy, double-check the numbers
- **Red (below 60%):** Low accuracy, review everything carefully

### Step 3: Fix Anything That's Wrong

Click on any field to edit it. Common things to check:
- Is the total correct?
- Is the vendor name spelled right?
- Are the dates right?

### Step 4: Save to Airtable

Click the **"Save to Airtable"** button.

You'll see a green checkmark when it's saved. Done!

*This takes about 30 seconds total per invoice.*

---

## What If Something Goes Wrong?

**The page is blank or won't load**
Try refreshing your browser (Ctrl+R or Cmd+R). If it's still blank, the app might be temporarily down. Try again in 10 minutes.

**"Failed to process" after uploading**
The PDF might be a scan (photo of paper) instead of a digital PDF. This tool only works with digital PDFs. Ask your vendor for a digital copy, or enter the invoice manually in Airtable.

**"Duplicate invoice" warning**
This invoice was already uploaded before. Check Airtable to see if it's already there.

**Numbers look wrong**
Click the field and type the correct value. Always double-check the total against the actual PDF before saving.

**Nothing happens when you click Upload**
Make sure the file is a PDF (ends in .pdf). The tool doesn't accept images, Word docs, or Excel files.

---

## Who to Contact for Help

- **Technical issues with the tool:** [AI Operations Lead]
- **Airtable questions:** [Admin name]
- **Invoice questions:** Sarah (Finance Lead)
