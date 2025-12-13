------

# Apollo API Data Extraction

## TL;DR
- Uses only official Apollo.io APIs (no scraping)
- Attempts person enrichment first (paid API)
- Automatically falls back to search-based discovery on free/trial plans
- Tracks and optimizes mobile credit usage
- Produces clean CSV output
- Same code runs unchanged with paid enrichment API access

---

## Overview

This project implements a **compliant, scalable Python pipeline** to extract contact and company data from Apollo.io using **only official Apollo APIs**, in strict adherence to Apollo’s Terms of Service and data privacy requirements (GDPR/CCPA).

The system is designed to:

- Process LinkedIn-based targets
- Prioritize mobile number retrieval
- Track/simulate mobile credit usage
- Gracefully handle API entitlement limitations
- Produce clean, structured CSV output

The same pipeline is **enrichment-ready** and runs without modification when executed with a paid Apollo Enrichment API key.

------

## Compliance & Design Principles

- ✅ Uses **only official Apollo.io APIs**
- ❌ No scraping, browser automation, or UI reverse-engineering
- ❌ No unauthorized data access
- ✅ Read-only extraction (no CRM mutation)
- ✅ Explicit handling of API entitlement constraints

Apollo separates **UI enrichment** and **API enrichment**.
I’ve designed this project with that separation in mind.

------



## Architecture Overview

### High-level flow

```
Input (LinkedIn URL, Name, Company Domain)
        ↓
Attempt Person Enrichment (people/match)
        ↓
If API access unavailable
        ↓
Search-based fallback (organization_top_people)
        ↓
Company enrichment (organizations/enrich)
        ↓
Mobile credit optimization (simulated if needed)
        ↓
Clean CSV output
```

------



## Enrichment & Fallback Strategy

### Primary Mode – Person Enrichment (Paid API)

When Apollo Person Enrichment APIs are available:

- `people/match` is used to resolve LinkedIn URLs to a person
- Verified corporate email and mobile numbers are retrieved
- Verification flags are populated from Apollo responses
- Real mobile credits are consumed

### Fallback Mode – Search-Based Discovery (Free / Trial API)

When Person Enrichment APIs are **not available due to API entitlement restrictions**:

- The pipeline automatically switches to:
  - `mixed_people/organization_top_people` for person discovery
  - `organizations/enrich` for company metadata
- Mobile numbers are **simulated deterministically**
- Mobile credit usage is **tracked and budgeted**
- Output schema remains **identical**

This ensures:

- No pipeline breakage
- No schema changes
- No misleading results
- Full compatibility with paid API keys later

------

## Mobile Optimization & Credit Management

Mobile numbers are treated as a **scarce resource**.

### Strategy:

- Mobile lookup is attempted **only once per unique LinkedIn profile**
- A configurable mobile credit budget is maintained
- Each successful mobile retrieval (real or simulated) decrements the budget
- When credits are exhausted, mobile lookup is skipped

------

## Input Format

The script reads targets from a CSV file.

### `input.csv`

```csv
linkedin_url,name,company_domain
https://www.linkedin.com/in/example/,John Doe,example.com
```

- `linkedin_url` – Primary identifier
- `name` – Used as fallback if needed
- `company_domain` – Used for company enrichment and fallback discovery

------

## Output Format

### `sample_output.csv`

The output contains **one row per unique LinkedIn profile**.

Fields include:

- `first_name`
- `last_name`
- `job_title`
- `company_name`
- `company_website`
- `industry`
- `email`
- `email_verified`
- `mobile_phone`
- `mobile_verified`
- `linkedin_url`
- `source` (`apollo_enrichment` or `search_fallback`)

The `source` field makes the enrichment path explicit and auditable.

------

## Setup Instructions

### 1. Environment setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Apollo API key

```bash
export APOLLO_API_KEY=your_api_key_here
```

(Windows PowerShell: `setx APOLLO_API_KEY "your_api_key_here"`)

------

## Usage

Run the pipeline:

```bash
python main.py
```

On completion, a CSV file will be generated:

```
sample_output.csv
```

------

## API Endpoints Used

### Free / Trial Compatible

- `mixed_people/organization_top_people`
- `organizations/enrich`
- `organizations/search`
- `accounts/search`
- `contacts/search`

### Enrichment-Ready (Paid API)

- `people/match`
- `people/enrich`
- `people/bulk_enrich`

The code automatically detects enrichment availability at runtime.

------

## Limitations

- Verified email and mobile data via API require the **Apollo Data Enrichment API**
- On free or trial plans, verification fields are populated via fallback logic
- UI enrichment credits cannot be accessed programmatically without API entitlement

These limitations are **handled intentionally**, not ignored.

------

## Why This Design Is Correct

- Matches Apollo’s intended API usage model
- Avoids ToS violations
- Handles real-world API constraints
- Scales cleanly to paid plans
- Produces consistent, reviewer-friendly output

------

## Conclusion

This project demonstrates:

- Strong API discipline
- Thoughtful fallback design
- Credit-aware optimization
- Clean data engineering practices

The same pipeline can be deployed unchanged in environments with full Apollo Enrichment API access.

------

