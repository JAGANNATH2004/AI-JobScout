from database.db import job_exists, insert_job
import logging

logger = logging.getLogger(__name__)

def deduplicate_and_store_jobs(jobs):
    """
    Remove duplicated links from the current batch and existing database links.
    Insert the fresh jobs into DB.
    """
    unique_jobs = []
    seen_links = set()
    
    for job in jobs:
        link = job.get('link')
        if not link:
            continue
            
        if link in seen_links:
            continue
            
        if job_exists(link):
            continue
            
        seen_links.add(link)
        unique_jobs.append(job)
        
    logger.info(f"Filtered {len(jobs)} total jobs down to {len(unique_jobs)} fresh jobs.")
    
    # Track them in DB now so they aren't processed again next run.
    inserted_count = 0
    for job in unique_jobs:
       if insert_job(job):
           inserted_count += 1
           
    logger.info(f"Inserted {inserted_count} new jobs into DB.")
    return unique_jobs
