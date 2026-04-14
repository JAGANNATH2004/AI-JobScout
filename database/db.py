import sqlite3
import logging
import sys
import os

# Ensure we can import from top level
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def init_db():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    experience TEXT,
                    link TEXT UNIQUE NOT NULL,
                    posted_time TEXT,
                    description TEXT,
                    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing DB: {e}")

def job_exists(link: str) -> bool:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM jobs WHERE link = ?', (link,))
            return cursor.fetchone() is not None
    except Exception as e:
        logger.error(f"Error checking if job exists: {e}")
        return False

def insert_job(job: dict):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO jobs (title, company, location, experience, link, posted_time, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                job.get('title', ''),
                job.get('company', ''),
                job.get('location', ''),
                job.get('experience', ''),
                job.get('link', ''),
                job.get('posted_time', ''),
                job.get('description', '')
            ))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        # Ignore duplicate errors from the UNIQUE constraint
        return False
    except Exception as e:
        logger.error(f"Error inserting job: {e}")
        return False
