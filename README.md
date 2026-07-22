# Company Contact Finder

Async bulk scraper that finds **website**, **email**, and **phone** for a list of companies, reading from and writing to Excel (`.xlsx`).

---

## Features

| Feature | Detail |
|---|---|
| **Speed** | 20 async workers → ~8–15 min for 1 000 companies |
| **Search** | Brave Search API (primary) + DuckDuckGo (fallback) |
| **Email sources** | `mailto:`, HTML, JSON-LD, Footer, Header, Script tags, Meta tags, obfuscated (`[at]`) |
| **Phone parsing** | Google's `phonenumbers` library – handles `+91`, `(080)`, `+1 800`, `0044 20 …` |
| **Contact pages** | Probes 15+ paths (`/contact`, `/about-us`, `/imprint`, …) + homepage link scan |
| **Resume** | Checkpoint in `checkpoint/progress.json` – restart after a crash from where you left off |
| **Auto-save** | Saves every 20 companies so at most 20 records are lost on a crash |
| **Retry logic** | Exponential back-off (up to 3 attempts per request) |
| **Rate limiting** | Per-domain delay (default 1.5 s) to avoid bans |
| **Logging** | `logs/crawler.log` (DEBUG) + console (INFO) |
| **Output** | Colour-coded Excel: green = all 3 found, yellow = partial, red = nothing |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> Python 3.10+ recommended.

### 2. Configure (optional)

Copy `.env` and edit as needed:

```
BRAVE_API_KEY=your_key_here   # optional but recommended
MAX_WORKERS=20
AUTOSAVE_INTERVAL=20
```

Get a free Brave Search API key at <https://api.search.brave.com/>.

### 3. Prepare input

Put your company list in `input/companies.xlsx`.  
The only required column is **`Company Name`**.  
Optional pre-filled columns: `Website`, `Email`, `Phone` (already-known values are preserved).

If the file doesn't exist a sample 5-row file is created automatically on first run.

### 4. Run

```bash
python main.py
```

Results are written to `output/companies_updated.xlsx`.

### 5. Resume after interruption

Just run again:

```bash
python main.py
```

It reads `checkpoint/progress.json` and skips companies already completed.

To start completely fresh:

```bash
python -c "from src.resume import reset_checkpoint; reset_checkpoint()"
python main.py
```

---

## Project Structure

```
company-contact-finder/
├── main.py              # Entry point & orchestrator
├── config.py            # All settings (reads .env)
├── requirements.txt
├── .env                 # Your local config (not committed)
│
├── input/
│   └── companies.xlsx   # Input: must have "Company Name" column
│
├── output/
│   └── companies_updated.xlsx   # Output (auto-created)
│
├── logs/
│   └── crawler.log      # Full debug log
│
├── checkpoint/
│   └── progress.json    # Resume state
│
└── src/
    ├── logger.py        # Logging setup
    ├── excel.py         # Read / write Excel
    ├── search.py        # Brave + DuckDuckGo website discovery
    ├── crawler.py       # Async HTTP fetcher with rate limiting
    ├── extractor.py     # Email & phone extraction
    ├── validator.py     # Pick best email / phone from candidates
    ├── resume.py        # Checkpoint load/save
    ├── worker.py        # Per-company pipeline
    └── utils.py         # Shared helpers
```

---

## Expected Accuracy

| Field | Expected |
|---|---|
| Website | ~95 % |
| Email | ~80 % |
| Phone | ~75 % |

---

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `BRAVE_API_KEY` | _(empty)_ | Brave Search API key (optional) |
| `MAX_WORKERS` | `20` | Concurrent async workers |
| `REQUEST_TIMEOUT` | `15` | Seconds per HTTP request |
| `RETRY_ATTEMPTS` | `3` | Retries per request |
| `RATE_LIMIT_DELAY` | `1.5` | Seconds between requests to same domain |
| `AUTOSAVE_INTERVAL` | `20` | Save output every N companies |
| `INPUT_FILE` | `input/companies.xlsx` | Input path |
| `OUTPUT_FILE` | `output/companies_updated.xlsx` | Output path |

---

## License

MIT
