# Documentation Guide

*What docs exist, who they're for, and where to start.*

---

## Start Here

| You are a... | Start with... |
|--------------|--------------|
| **Finance team member** who needs to upload invoices | [Invoice Web App Quick Start](quick-starts/Invoice_Web_App_Quick_Start.md) |
| **HR team member** managing new hires | [HR Dashboard Quick Start](quick-starts/HR_Dashboard_Quick_Start.md) |
| **Operator** running automations from the command line | [Invoice Processor Runbook](runbooks/Invoice_Processor_Runbook.md) |
| **New maintainer** taking over these systems | [Handoff Document](Handoff_Document.md) |
| **Developer** extending or modifying automations | Root [CLAUDE.md](../CLAUDE.md) playbook |
| **Stakeholder** with questions | [FAQ](training/FAQ.md) |

---

## All Documentation

### Runbooks (For Operators & Maintainers)

Step-by-step guides for running and troubleshooting each automation.

| Runbook | Automation | Key Info |
|---------|-----------|----------|
| [Invoice Processor](runbooks/Invoice_Processor_Runbook.md) | Batch PDF processing | Setup, commands, common errors, emergency fallback |
| [Drive Automation](runbooks/Drive_Automation_Runbook.md) | Google Drive file watcher | OAuth setup, folder structure, monitoring |
| [Web App](runbooks/Web_App_Runbook.md) | Invoice upload web interface | Vercel deployment, env vars, redeployment |
| [HR Onboarding](runbooks/HR_Onboarding_Runbook.md) | Onboarding dashboard | CLI + web modes, template management |

### Quick Start Guides (For End Users)

Simple, jargon-free guides for non-technical team members.

| Guide | For | What It Covers |
|-------|-----|---------------|
| [Invoice Web App](quick-starts/Invoice_Web_App_Quick_Start.md) | Finance team | Upload, review, save invoices |
| [HR Dashboard](quick-starts/HR_Dashboard_Quick_Start.md) | HR team | Add hires, generate docs, track progress |

### Training & Reference (For Everyone)

| Document | Purpose |
|----------|---------|
| [FAQ](training/FAQ.md) | Answers to common questions (general, technical, user, business) |
| [Maintenance Guide](training/Maintenance_Guide.md) | Daily/weekly/monthly/quarterly/annual maintenance tasks |

### Handoff & Architecture

| Document | Purpose |
|----------|---------|
| [Handoff Document](Handoff_Document.md) | Everything a new maintainer needs to get started |
| [CLAUDE.md](../CLAUDE.md) | Architecture decisions, patterns, limitations, extension guide |
| [README.md](../README.md) | Project overview and setup instructions |

---

## Keeping Docs Updated

Documentation should evolve with the automations:

- When you fix a bug, update the relevant runbook's troubleshooting section
- When someone asks a new question, add it to the FAQ
- When you deploy changes, update URLs and commands in affected docs
- When you complete maintenance, log it

**The docs are only as good as their last update.**
