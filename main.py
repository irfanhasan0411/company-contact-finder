"""
main.py - Entry point for company-contact-finder
"""

from __future__ import annotations

import asyncio
import logging
import sys
import time
from typing import List

from tqdm.asyncio import tqdm

import config
from config import (
    INPUT_FILE, OUTPUT_FILE, LOG_FILE,
    MAX_WORKERS, AUTOSAVE_INTERVAL,
    COL_COMPANY, COL_WEBSITE, COL_EMAIL, COL_PHONE, COL_STATUS,
)
from src.crawler import make_session
from src.excel import read_companies, write_companies, create_sample_input
from src.logger import setup_logger
from src.resume import load_completed, mark_done
from src.worker import process_company

log = logging.getLogger("crawler")


async def run() -> None:
    setup_logger(LOG_FILE)
    log.info("=" * 60)
    log.info("Company Contact Finder – starting")
    log.info("=" * 60)

    # Ensure input file exists
    create_sample_input(INPUT_FILE)

    # Load rows and checkpoint
    rows = read_companies(INPUT_FILE)
    completed = load_completed()

    pending = [r for r in rows if r[COL_COMPANY] not in completed]
    log.info("Total: %d | Already done: %d | Pending: %d",
             len(rows), len(completed), len(pending))

    if not pending:
        log.info("Nothing to do – all companies already processed.")
        write_companies(rows, OUTPUT_FILE)
        return

    # Build a quick lookup: company name → row index in `rows`
    name_to_idx = {r[COL_COMPANY]: i for i, r in enumerate(rows)}

    semaphore = asyncio.Semaphore(MAX_WORKERS)
    processed_since_save = 0
    start_time = time.monotonic()

    async with make_session() as session:

        async def handle_one(row: dict) -> None:
            nonlocal processed_since_save

            company = row[COL_COMPANY]
            async with semaphore:
                website, email, phone, status = await process_company(
                    session,
                    company,
                    existing_website=row.get(COL_WEBSITE, "") or "",
                    existing_email=row.get(COL_EMAIL, "") or "",
                    existing_phone=row.get(COL_PHONE, "") or "",
                )

            # Write results back into the shared rows list
            idx = name_to_idx[company]
            rows[idx][COL_WEBSITE] = website or rows[idx].get(COL_WEBSITE, "")
            rows[idx][COL_EMAIL]   = email   or rows[idx].get(COL_EMAIL, "")
            rows[idx][COL_PHONE]   = phone   or rows[idx].get(COL_PHONE, "")
            rows[idx][COL_STATUS]  = status

            mark_done(company, completed)
            processed_since_save += 1

            # Auto-save every AUTOSAVE_INTERVAL companies
            if processed_since_save >= AUTOSAVE_INTERVAL:
                write_companies(rows, OUTPUT_FILE)
                processed_since_save = 0
                log.info("Auto-saved after %d companies", AUTOSAVE_INTERVAL)

        tasks = [handle_one(row) for row in pending]

        # tqdm progress bar over gathered tasks
        for coro in tqdm(
            asyncio.as_completed(tasks),
            total=len(tasks),
            desc="Processing",
            unit="co",
            ncols=90,
            file=sys.stdout,
        ):
            await coro

    # Final save
    write_companies(rows, OUTPUT_FILE)

    elapsed = time.monotonic() - start_time
    mins, secs = divmod(int(elapsed), 60)
    done_count = len(completed)
    found_web   = sum(1 for r in rows if r.get(COL_WEBSITE))
    found_email = sum(1 for r in rows if r.get(COL_EMAIL))
    found_phone = sum(1 for r in rows if r.get(COL_PHONE))

    log.info("=" * 60)
    log.info("Finished in %dm %ds", mins, secs)
    log.info("Companies processed : %d", done_count)
    log.info("Websites found      : %d (%.0f%%)", found_web,   100*found_web/max(done_count,1))
    log.info("Emails found        : %d (%.0f%%)", found_email, 100*found_email/max(done_count,1))
    log.info("Phones found        : %d (%.0f%%)", found_phone, 100*found_phone/max(done_count,1))
    log.info("Output saved to     : %s", OUTPUT_FILE)
    log.info("=" * 60)


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        log.warning("Interrupted by user – progress has been saved to checkpoint.")
        sys.exit(0)


if __name__ == "__main__":
    main()
