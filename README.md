# ga4-gtm-audit-checker

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

A command-line audit tool for Google Analytics 4 and Google Tag Manager setups. Identifies missing conversion events, broken tags, misconfigured triggers, and tracking gaps before they cost you campaign performance.

## The Problem

Most GA4 and GTM setups have silent failures — events that fire on the wrong pages, conversions that never get counted, or tags that break after a CMS update. By the time you notice, you've made decisions on bad data.

## What It Does

- Connects to GA4 via the Data API and checks for expected event coverage
- Connects to GTM API and lists all tags, firing status, and last modified date
- Flags tags that haven't fired in 30+ days
- Reports missing standard events (purchase, add_to_cart, generate_lead, etc.)
- Exports a clean audit report as CSV or JSON

## Features

- ✅ GA4 event coverage check against a customizable expected-events list
- ✅ GTM tag inventory with last-fired timestamps
- ✅ Flags paused tags, tags with no firing triggers, and duplicate tags
- ✅ Cross-checks GA4 conversions against GTM conversion tags
- ✅ Outputs audit report to CSV, JSON, or terminal
- ✅ Works with multiple GA4 properties and GTM containers

## Tech Stack

- Python 3.9+
- Google Analytics Data API
- Google Tag Manager API
- pandas for report generation

## Installation

```bash
git clone https://github.com/mehranmoghadasi/ga4-gtm-audit-checker
cd ga4-gtm-audit-checker
pip install -r requirements.txt
cp .env.example .env
```

## Usage

```bash
# Full audit
python audit.py --property YOUR_GA4_PROPERTY_ID --container YOUR_GTM_CONTAINER_ID

# Export to CSV
python audit.py --property YOUR_GA4_PROPERTY_ID --output csv

# Events only
python audit.py --property YOUR_GA4_PROPERTY_ID --events-only
```

## Sample Output

```
GA4 + GTM Audit Report — 2026-04-24
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ page_view      — firing correctly
✅ session_start  — firing correctly
❌ purchase       — NOT found in last 30 days
❌ generate_lead  — NOT found in last 30 days
GTM Tags: 14 active | 3 paused | 2 never fired
Report saved to: audit_2026-04-24.csv
```

## License

MIT
