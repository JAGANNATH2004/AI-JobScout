# AI Job Scraper & Ranker Pipeline

An end-to-end automated job scraping pipeline that fetches fresher-level AI/ML and Data Science jobs from LinkedIn and Naukri, filters them, ranks them using a local LLM (Ollama), and delivers a curated list of top roles straight to your Telegram daily.

## 🚀 Key Features

*   **Multi-Source Scraping:** Scrapes job postings autonomously from multiple platforms (LinkedIn, Naukri) tailored to specific hubs (Hyderabad, Bangalore, Chennai).
*   **Smart Filtering:** Pre-filters jobs for 0-1 years of experience and matches relevant titles (AI, ML, Data Science).
*   **Intelligent Ranking (Local LLM):** Leverages local AI models using **Ollama** to contextually evaluate and rank the *top 9* most suitable jobs from the daily batch. 
    *   **CPU Friendly:** Capable of running lightweight models (like `gemma3:4b` or the 4-billion parameter variants) which are explicitly suitable to run on almost any system with minimal CPU requirements and absolutely **no need for a dedicated GPU**. No API keys or external cloud costs required!
*   **Deduplication:** Utilises an **SQLite** database to remember previously seen jobs, ensuring you are never notified about the same job post twice.
*   **Automated Scheduling:** Runs autonomously in the background using `APScheduler`. Scrapes for jobs periodically and dispatches a single, consolidated digest message at a configured time every day.
*   **Telegram Integration:** Delivers the finalized list directly to your phone via a Telegram Bot, nicely formatted for quick viewing.

## 🛠️ Tech Stack
*   **Language:** Python 3
*   **Scraping:** Requests / BeautifulSoup (or specific scrapers based on module implementation)
*   **Local AI Inference:** [Ollama](https://ollama.com/)
*   **Model:** `gemma4:e4b`
*   **Database:** SQLite (`jobs.db`)
*   **Task Scheduling:** `apscheduler`

## 📋 Prerequisites
1.  **Python 3.8+** installed.
2.  **Ollama** installed on your system.
3.  A **Telegram Bot Token** and your **Chat ID**. (Talk to `BotFather` on Telegram to create a bot).

## ⚙️ Setup & Installation

**1. Clone the repository and navigate to the folder.**

**2. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**3. Download the LLM using Ollama:**
Make sure Ollama is running, then pull the model required for ranking:
```bash
ollama pull gemma4:e4b
```

**4. Environment Variables Setup:**
Create a `.env` file in the root directory and add the following keys:
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN="your_bot_token_here"
TELEGRAM_CHAT_ID="your_chat_id_here"

# Ollama LLM Configuration (Optional defaults)
OLLAMA_HOST="http://localhost:11434"
OLLAMA_MODEL="gemma4:e4b"

# SQLite Database
DATABASE_PATH="jobs.db"
```

## 💻 Usage

**1. Ensure your local Ollama server is running:**
*(On Windows, Ollama generally runs quietly in the system tray automatically, but you can explicitly start it if needed).*
```bash
ollama serve
```

**2. Start the Job Scraper Pipeline:**
```bash
python main.py
```

### What happens when you run `main.py`?
1.  **Initialization:** The local SQLite database (`jobs.db`) is set up to track unique job links.
2.  **Startup Cycle:** It immediately runs an initial job scraping cycle fetching from LinkedIn and Naukri.
3.  **Filtration:** Filters jobs down matching the 0-1 yr exp criteria and deduplicates them using the database.
4.  **Scheduler Backgrounding:** Sits in the background. It will scrape fresh jobs roughly every 23 hours. 
5.  **Daily Report:** At the scheduled time (e.g., 07:12 PM IST), it passes the daily cached fresh jobs to your local Ollama model to rank the **top 9** opportunities, then blasts the result via the Telegram Bot. The cache is then cleared for the next cycle.

## 🧠 Adjusting the AI Ranking Prompt
You can tweak how the LLM evaluates jobs by modifying the `prompt_template.txt` located in the `llm/` directory.

## 🔧 Troubleshooting
*   **Ollama Connection Error:** Ensure `ollama serve` is running and the port `11434` is accessible.
*   **0 Fresh Jobs added?** If testing, you might have already populated your database with jobs. To test a fresh run and bypass deduplication, simply delete your `jobs.db` file and run `main.py` again.
*   **Model Too Slow / Memory Issues?** If you are running on CPU without dedicated VRAM, ensure you are utilizing a lightweight model like `gemma3:4b` instead of heavy memory ones that swap to disk. You can update this in `config.py` and `.env`.
