import requests
from bs4 import BeautifulSoup
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logger = logging.getLogger(__name__)

# Naukri city slugs for URL construction
# Format: https://www.naukri.com/<role>-jobs-in-<city-slug>
CITY_URLS = [
    {
        "city": "Hyderabad",
        "url": "https://www.naukri.com/ai-ml-data-science-fresher-jobs-in-hyderabad?experience=0&experience=1&sort=r"
    },
    {
        "city": "Bangalore",
        "url": "https://www.naukri.com/ai-ml-data-science-fresher-jobs-in-bangalore?experience=0&experience=1&sort=r"
    },
    {
        "city": "Chennai",
        "url": "https://www.naukri.com/ai-ml-data-science-fresher-jobs-in-chennai?experience=0&experience=1&sort=r"
    },
]

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}


def _scrape_city(city: str, url: str) -> list:
    """Scrape one Naukri city URL and return list of job dicts."""
    jobs = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try both old and new Naukri article/div class layouts
        articles = soup.find_all('article', class_='jobTuple', limit=20)
        if not articles:
            articles = soup.find_all('div', class_='srp-jobtuple-wrapper', limit=20)

        logger.info(f"Naukri [{city}]: {len(articles)} job cards found.")

        for article in articles:
            try:
                title_tag    = article.find('a', class_='title') or article.find('a', class_='title ')
                company_tag  = article.find('a', class_='comp-name')
                location_tag = article.find('span', class_='locWdth')
                exp_tag      = article.find('span', class_='expwdth')
                posted_tag   = article.find('span', class_='job-post-day')

                if not title_tag:
                    continue

                title       = title_tag.get_text(strip=True)
                link        = title_tag.get('href', '').split('?')[0]
                company     = company_tag.get_text(strip=True)  if company_tag  else ''
                location    = location_tag.get_text(strip=True) if location_tag else city
                experience  = exp_tag.get_text(strip=True)      if exp_tag      else '0-2 Yrs'
                posted_time = posted_tag.get_text(strip=True)   if posted_tag   else 'Recently'

                if title and link:
                    jobs.append({
                        "title":       title,
                        "company":     company,
                        "location":    location,
                        "experience":  experience,
                        "posted_time": posted_time,
                        "link":        link,
                        "description": "Details available via link"
                    })

            except Exception as e:
                logger.debug(f"Error parsing Naukri card ({city}): {e}")

    except Exception as e:
        logger.error(f"Naukri scrape failed for city '{city}': {e}")

    return jobs


def scrape_naukri_jobs():
    """
    Scrape Naukri for AI/ML fresher jobs (0-2 years) in
    Hyderabad, Bangalore, and Chennai.
    """
    all_jobs = []

    for entry in CITY_URLS:
        city_jobs = _scrape_city(entry["city"], entry["url"])
        all_jobs.extend(city_jobs)
        logger.info(f"Naukri [{entry['city']}]: collected {len(city_jobs)} jobs.")

    logger.info(f"Naukri total: {len(all_jobs)} jobs across all cities.")
    return all_jobs
