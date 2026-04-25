# AntiGravity Lead Generation System

A high-scale lead generation engine in Python designed to identify businesses that require websites and WhatsApp automation services. It evaluates their digital presence and prioritizes them as targets for digital agencies.

## Features
- **Headless Chrome Scraping** using Playwright.
- **Infinite Scrolling & Pagination** natively supported via human-like actions.
- **Data Qualification Algorithm** scoring leads 0-100 based on website presence, review activity, and unprofessional emails.
- **WhatsApp Automation Detection** and personalized WA marketing message generation.
- **MongoDB** integration for phone and website deduplication.
- **CSV & Excel Outputs** for easy spreadsheet import.

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- MongoDB (Optional, for deduplicating saved records if running multiple times)

### 2. Environment Initialization
```bash
# Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

### 3. Execution (Example Run)
You can run the script indicating the `city`, the `category` and the maximum amount of leads to gather `--max`.

```bash
# Example: Gather Plumber leads in London
python main.py --city "London" --category "Plumbers" --max 10

# Example: Gathering fitness gyms
python main.py --city "New York" --category "Gyms" --max 50
```

## Modular Architecture (`src/`)
- `scrapers/`: The extractors fetching raw data. `google_maps.py` implements a complex Playwright crawler solving the infinite scroll list.
- `processors/`: Business logic. 
  - `qualifier.py` scores the leads based on absence of website or unprofessional presence.
  - `whatsapp.py` detects indicators of WA presence.
  - `formatter.py` dynamically formats personalized WhatsApp outreach templates.
- `storage/`: Persisting information. `db.py` uses AsyncIOMotor to dump un-duplicated data to MongoDB. `exporter.py` builds the CSV structure, sorted algorithmically by lead priority.
