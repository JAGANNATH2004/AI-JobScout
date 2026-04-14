import logging
import sys

from config import logger
from database.db import init_db
from scraper.linkedin_scraper import scrape_linkedin_jobs
from scraper.naukri_scraper import scrape_naukri_jobs
from processor.filter_jobs import filter_basic_jobs
from processor.deduplicator import deduplicate_and_store_jobs
from processor.ranker import get_top_jobs
from notifier.telegram_bot import send_telegram_message
from scheduler.scheduler import start_scheduler

# Central store for jobs collected over the day
DAILY_JOBS_CACHE = []


def run_scraping_cycle():
    """Scrapes jobs, filters, deduplicates, stores in DB, and adds to daily cache."""
    global DAILY_JOBS_CACHE
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("Starting scraping cycle...")

    linkedin_jobs = scrape_linkedin_jobs()
    naukri_jobs   = scrape_naukri_jobs()

    all_jobs = linkedin_jobs + naukri_jobs
    logger.info(f"Scraped {len(all_jobs)} raw jobs (LinkedIn: {len(linkedin_jobs)}, Naukri: {len(naukri_jobs)})")

    valid_jobs = filter_basic_jobs(all_jobs)
    fresh_jobs = deduplicate_and_store_jobs(valid_jobs)

    DAILY_JOBS_CACHE.extend(fresh_jobs)
    logger.info(f"Cycle complete. {len(fresh_jobs)} fresh jobs added. Cache size: {len(DAILY_JOBS_CACHE)}")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


def send_daily_notification():
    """Ranks cached jobs via Ollama, sends to Telegram, then clears the cache."""
    global DAILY_JOBS_CACHE
    logger.info("Executing daily notification routine...")

    if not DAILY_JOBS_CACHE:
        logger.warning("No jobs in cache — sending empty notification.")

    top_9_jobs = get_top_jobs(DAILY_JOBS_CACHE)
    send_telegram_message(top_9_jobs)

    DAILY_JOBS_CACHE.clear()
    logger.info("Daily notification sent. Cache cleared for the next 24h cycle.")


if __name__ == "__main__":
    logger.info("═══════════════════════════════════════════════════════")
    logger.info("  Job Scraper Agent — Starting Up")
    logger.info("═══════════════════════════════════════════════════════")

    # Step 1 — Initialise SQLite database
    init_db()

    # Step 2 — Run first scraping cycle IMMEDIATELY on startup
    logger.info("Running initial scraping cycle on startup...")
    run_scraping_cycle()

    # Step 3 — Hand off to scheduler:
    #   • Scrape again every 23 hours
    #   • Notify via Telegram daily at 9:15 PM IST
    start_scheduler(run_scraping_cycle, send_daily_notification)