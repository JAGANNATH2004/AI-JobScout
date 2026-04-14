import re
import logging

logger = logging.getLogger(__name__)

# ── Target locations ──────────────────────────────────────────────────────────
TARGET_CITIES = ['hyderabad', 'bangalore', 'bengaluru', 'chennai']

# ── Target job title keywords ─────────────────────────────────────────────────
JOB_KEYWORDS = [
    'data', 'machine learning', 'ml', 'ai', 'artificial intelligence',
    'scientist', 'python', 'analyst', 'deep learning', 'nlp',
    'computer vision', 'llm', 'generative', 'neural', 'analytics'
]

# ── Fresher/entry-level synonyms that are always accepted ────────────────────
FRESHER_TERMS = ['fresher', 'fresh', 'entry', 'intern', 'trainee', 'graduate']


def _is_within_experience(experience_str: str) -> bool:
    """
    Returns True if the job's experience requirement is 0-1 year.

    Accepted examples:
      "0-1 Yrs", "0-1 year", "fresher", "entry level",
      "0 Yrs", "1 Yrs", "trainee", "graduate"
    Rejected examples:
      "1-3 Yrs", "2-4 Yrs", "3+ years", "5 years"
    """
    exp = experience_str.lower().strip()

    # Always accept if experience field is empty/unknown
    if not exp:
        return True

    # Accept obvious fresher synonyms
    if any(term in exp for term in FRESHER_TERMS):
        return True

    # Extract all numbers from the string
    numbers = [int(n) for n in re.findall(r'\d+', exp)]

    if not numbers:
        # No numbers found — treat as unknown, keep it
        return True

    # The *minimum* required experience is numbers[0]
    # The *maximum* required experience is the last number
    max_exp = numbers[-1]

    # Reject anything requiring more than 1 year
    return max_exp <= 1


def filter_basic_jobs(jobs):
    """
    Three-stage pre-filter before sending to Ollama:

    Stage 1 — Link check:      Must have a non-empty link.
    Stage 2 — Title keywords:  Must match at least one AI/ML/Data keyword.
    Stage 3 — Location:        Must be in Hyderabad, Bangalore, or Chennai.
    Stage 4 — Experience:      Must require 0-1 year (freshers only).
    """
    relevant_jobs = []

    for job in jobs:
        title      = job.get('title', '').lower()
        location   = job.get('location', '').lower()
        experience = job.get('experience', '')
        link       = job.get('link', '').strip()

        # Stage 1 — link
        if not link:
            logger.debug(f"Dropped (no link): '{job.get('title')}'")
            continue

        # Stage 2 — title keyword
        if not any(kw in title for kw in JOB_KEYWORDS):
            logger.debug(f"Dropped (title): '{job.get('title')}'")
            continue

        # Stage 3 — location (allow blank location through)
        if location and not any(city in location for city in TARGET_CITIES):
            logger.debug(f"Dropped (location '{job.get('location')}'): '{job.get('title')}'")
            continue

        # Stage 4 — experience
        if not _is_within_experience(experience):
            logger.debug(f"Dropped (exp '{experience}'): '{job.get('title')}'")
            continue

        relevant_jobs.append(job)

    logger.info(
        f"Filter: {len(jobs)} scraped → {len(relevant_jobs)} kept "
        f"(0-1 yr exp | Hyderabad / Bangalore / Chennai | AI/ML roles)"
    )
    return relevant_jobs
