from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import pytz

logger = logging.getLogger(__name__)

IST = pytz.timezone('Asia/Kolkata')


def start_scheduler(scrape_job_func, notify_job_func):
    """
    Starts the APScheduler blocking scheduler.

    Schedule:
      - scrape_job_func : runs every 23 hours (after the initial immediate run in main.py)
      - notify_job_func : runs once daily at 21:15 IST (9:15 PM)
    """
    scheduler = BlockingScheduler(timezone=IST)

    # ── Scraping every 23 hours ──────────────────────────────────────────────
    scheduler.add_job(
        scrape_job_func,
        'interval',
        hours=23,
        id='scrape_jobs_interval',
        name='Scrape Jobs (every 23h)'
    )

    scheduler.add_job(
        notify_job_func,
        CronTrigger(hour=18, minute=0, timezone=IST),
        id='send_daily_notification',
        name='Send Telegram Notification (18:00 IST)'
    )
    logger.info(
        "Scheduler started.\n"
        "  ▸ Scraping          : every 23 hours\n"
        "  ▸ Telegram notify   : daily at 06:00 PM IST"
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")