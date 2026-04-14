import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm.ollama_client import evaluate_jobs_with_ollama

logger = logging.getLogger(__name__)


def get_top_jobs(jobs):
    """
    Sends all fresh jobs to the local Ollama model for ranking.
    Returns the top 9 most relevant entry-level AI/ML jobs.
    Falls back to the first 9 unranked jobs if Ollama fails.
    """
    if not jobs:
        logger.info("No jobs in cache to rank.")
        return []

    logger.info(f"Sending {len(jobs)} jobs to Ollama for ranking...")

    # Cap at 60 to avoid overwhelming the context window
    MAX_TO_SEND = 60
    jobs_to_evaluate = jobs[:MAX_TO_SEND]

    try:
        top_jobs = evaluate_jobs_with_ollama(jobs_to_evaluate)

        # Enforce max 9
        top_jobs = top_jobs[:9]
        logger.info(f"Final ranked list: {len(top_jobs)} jobs.")
        return top_jobs

    except Exception as e:
        logger.error(f"Ranking failed entirely: {e}. Using first 9 unranked jobs.")
        return jobs[:9]
