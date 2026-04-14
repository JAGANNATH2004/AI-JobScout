import requests
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

TELEGRAM_MAX_CHARS = 4096  # Telegram hard limit per message


def _send_single_message(text: str):
    """
    Send one message chunk via Telegram Bot API (POST with JSON body).
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    }
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()


def send_telegram_message(jobs):
    """
    Format and send top jobs to Telegram.
    Automatically splits into multiple messages if content
    exceeds Telegram's 4096-character limit.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram credentials missing. Cannot send notification.")
        return

    # ── No jobs case ──────────────────────────────────────────────────────────
    if not jobs:
        try:
            _send_single_message("🔍 No new AI/ML Fresher jobs found in the last 24 hours.")
            logger.info("Sent empty-result notification to Telegram.")
        except Exception as e:
            logger.error(f"Failed to send empty notification: {e}")
        return

    # ── Build individual job blocks ───────────────────────────────────────────
    header = f"🔥 Top {len(jobs)} Fresher AI/ML Jobs — Last 24 Hours\n\n"

    job_blocks = []
    for i, job in enumerate(jobs, 1):
        title    = job.get('title', 'N/A').strip()
        company  = job.get('company', 'N/A').strip()
        location = job.get('location', 'Remote/India').strip()
        posted   = job.get('posted_time', 'Recently').strip()
        link     = job.get('link', '').strip()

        # Skip jobs with no link (should never happen after validation but safety net)
        if not link:
            continue

        block = (
            f"{i}. {title}\n"
            f"🏢 {company}\n"
            f"📍 {location} | 🕒 {posted}\n"
            f"🔗 {link}\n\n"
        )
        job_blocks.append(block)

    if not job_blocks:
        _send_single_message("⚠️ Jobs were ranked but none had valid links.")
        return

    # ── Chunk into messages under 4096 chars ─────────────────────────────────
    chunks  = []
    current = header

    for block in job_blocks:
        if len(current) + len(block) > TELEGRAM_MAX_CHARS:
            chunks.append(current.strip())
            current = block
        else:
            current += block

    if current.strip():
        chunks.append(current.strip())

    # ── Send each chunk ───────────────────────────────────────────────────────
    total = len(chunks)
    for idx, chunk in enumerate(chunks, 1):
        try:
            _send_single_message(chunk)
            logger.info(f"Telegram message sent ({idx}/{total}).")
        except Exception as e:
            logger.error(f"Failed to send Telegram part {idx}/{total}: {e}")
