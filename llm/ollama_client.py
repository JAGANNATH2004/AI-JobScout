import requests
import logging
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OLLAMA_HOST, OLLAMA_MODEL

logger = logging.getLogger(__name__)


def evaluate_jobs_with_ollama(jobs_batch):
    """
    Sends a batch of jobs to the local Ollama model.
    Returns a list of up to 9 top-ranked job dicts.
    """
    if not jobs_batch:
        return []

    try:
        template_path = os.path.join(os.path.dirname(__file__), "prompt_template.txt")
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()

        jobs_json = json.dumps(jobs_batch, indent=2)
        prompt = template.replace("{jobs_json}", jobs_json)

        logger.info(f"Calling Ollama model '{OLLAMA_MODEL}' at {OLLAMA_HOST} ...")

        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "stream": False,
                # NOTE: do NOT set "format": "json" here — it forces a JSON *object*
                # which causes the model to invent wrapper keys unpredictably.
                # We control the output format entirely through the prompt instead.
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful AI recruiting assistant. "
                            "You ONLY output a valid JSON object with a single key 'jobs'. "
                            "No markdown fences. No explanation. Pure JSON only."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            timeout=600  # gemma4 is large; allow up to 10 min for local inference
        )
        response.raise_for_status()

        result = response.json()
        response_text = result.get("message", {}).get("content", "").strip()

        # Strip accidental markdown fences if model adds them
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].strip()

        parsed = json.loads(response_text)

        # Primary: expect {"jobs": [...]}
        if isinstance(parsed, dict):
            top_jobs = (
                parsed.get("jobs")
                or parsed.get("results")
                or parsed.get("job_postings")
                or next((v for v in parsed.values() if isinstance(v, list)), None)
            )
            if top_jobs is None:
                logger.warning("Ollama returned a dict but no list found inside. Using fallback.")
                return jobs_batch[:9]
        elif isinstance(parsed, list):
            top_jobs = parsed
        else:
            logger.warning("Unexpected Ollama response type. Using fallback.")
            return jobs_batch[:9]

        # Validate that returned jobs actually have required fields
        valid_jobs = []
        for job in top_jobs:
            if isinstance(job, dict) and job.get("title") and job.get("link"):
                valid_jobs.append(job)

        if not valid_jobs:
            logger.warning("Ollama returned jobs with missing fields. Using original batch as fallback.")
            return jobs_batch[:9]

        logger.info(f"Ollama returned {len(valid_jobs)} valid ranked jobs.")
        return valid_jobs

    except requests.exceptions.ConnectionError:
        logger.error(
            f"Cannot connect to Ollama at {OLLAMA_HOST}. "
            "Make sure Ollama is running: `ollama serve`"
        )
        return jobs_batch[:9]
    except json.JSONDecodeError as e:
        logger.error(f"Ollama response was not valid JSON: {e}")
        return jobs_batch[:9]
    except Exception as e:
        logger.error(f"Error calling Ollama API: {e}")
        return jobs_batch[:9]
