"""
config.py - Central configuration for company-contact-finder
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).parent
INPUT_FILE      = BASE_DIR / os.getenv("INPUT_FILE",  "input/companies.xlsx")
OUTPUT_FILE     = BASE_DIR / os.getenv("OUTPUT_FILE", "output/companies_updated.xlsx")
LOG_FILE        = BASE_DIR / "logs/crawler.log"
CHECKPOINT_FILE = BASE_DIR / "checkpoint/progress.json"

# ── API keys ───────────────────────────────────────────────────────────────────
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "").strip()

# ── Concurrency & networking ───────────────────────────────────────────────────
MAX_WORKERS      = int(os.getenv("MAX_WORKERS",      20))
REQUEST_TIMEOUT  = int(os.getenv("REQUEST_TIMEOUT",  15))
RETRY_ATTEMPTS   = int(os.getenv("RETRY_ATTEMPTS",    3))
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", 1.5))

# ── Auto-save ──────────────────────────────────────────────────────────────────
AUTOSAVE_INTERVAL = int(os.getenv("AUTOSAVE_INTERVAL", 20))

# ── Contact page paths to probe ────────────────────────────────────────────────
CONTACT_PATHS = [
    "/contact",
    "/contact-us",
    "/contacts",
    "/about",
    "/about-us",
    "/support",
    "/company",
    "/imprint",
    "/impressum",
    "/legal",
    "/privacy",
    "/team",
    "/office",
    "/reach-us",
    "/get-in-touch",
]

# ── HTTP headers ───────────────────────────────────────────────────────────────
DEFAULT_HEADERS = {
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection":      "keep-alive",
    "DNT":             "1",
}

# ── Phone extraction ───────────────────────────────────────────────────────────
# Country codes to try when parsing ambiguous numbers (add yours first)
PHONE_REGIONS = ["IN", "US", "GB", "AU", "SG", "AE", "CA", "DE"]

# ── Excel column names ─────────────────────────────────────────────────────────
COL_COMPANY = "Company Name"
COL_WEBSITE = "Website"
COL_EMAIL   = "Email"
COL_PHONE   = "Phone"
COL_STATUS  = "Status"
