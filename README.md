# Motivation

After settling in the UK for a year, I unexpectedly found myself registered for the UTS 100K (Ultra Trail Snowdonia Eryri by UTMB)—thanks to my wife, who signed me up without much say in the matter. Despite dealing with multiple injuries and a lack of recent racing experience, my ITRA index still stands at 772, but it's set to expire soon if I don’t compete.

As an opportunity to explore machine learning and AI, I decided to analyze UTMB runners, race data, and ranking systems. This project uses Python’s scikit-learn to develop predictive models, data visualization, and race recommendations to help determine the best competitions for performance improvement.

To enhance race predictions, I also integrated Strava data, allowing runners to analyse their training patterns, fitness trends, and race preparedness. By combining historical race results, training logs, and real-time performance metrics, this platform can provide personalised race recommendations and coaching insights.

I also built a frontend using ReactJS and TailwindCSS, as well as JavaScript libraries such as HighchartsJS and LeafletJS which I’m familiar with from my time at the Hong Kong Observatory. This project will continue evolving, with plans for additional tools and features to enhance its utility for runners and race organizers.

I named it UltraRunAI at a start.

## Technologies Planned to Use

- **Python (Selenium, BeautifulSoup, Pandas, Scikit-Learn)**
- **Machine Learning (Regression, Clustering, Recommendation Systems)**
- **React + TailwindCSS + HighchartJS + LeafletJS (Frontend UI)**
- **Flask (Backend API)**
- **PostgreSQL (Database)**

## **Web Scraping: Collecting Ultra-Trail Race and Runner Data Using Selenium**

Extracting **UTMB runner and race data** from [UTMB Runner Search](https://utmb.world/utmb-index/runner-search/), using **Selenium** for automated browsing and **BeautifulSoup** for data extraction.

---

### 1. Overview of the Scraping Process

#### Runner Scraper

1. **`runner_id_scraper.py`**

   - Scrapes **all runner IDs** from the UTMB website.
   - Saves runner IDs in **timestamped JSON files**.
   - Supports incremental updates.

2. **`split_runner_id.py`**

   - Splits the **full runner ID list** into smaller JSON files.

3. **`runner_scraper.py`**
   - Uses the split JSON files to scrape **detailed runner profiles**.

#### Race Scraper

4. **`race_scraper.py`**
   - Scrapes **UTMB race results** from a given range of race UIDs and years.
   - Saves race results in **JSON format**.

#### Clean data

5. **`clean.py`**
   - Concatenates data inside the raw JSON folders.
   - Removes duplicates and preserves the latest data.

---

### 2. Usage Instructions

Run the full scraping process for 3M+ runners incrementally:

```bash
cd webapps/backend/scraping
./scrape_all_runners.sh
```

Run the full scraping process for 40,000+ races incrementally:

```bash
cd webapps/backend/scraping
./scrape_all_races.sh
```

---

### 3. Script-Specific Usage

#### `runner_id_scraper.py` – Extract Runner IDs

```bash
python3 runner_id_scraper.py <NUM_PAGES>
```

- `<NUM_PAGES>`: Number of pages to scrape (use `"max"` for all pages).
- Example:

```bash
python3 runner_id_scraper.py "max"
```

- Output:
  - Saves runner IDs to `../../frontend/public/data/raw_runner_id_data/runner_id_YYYYMMDDHHMMSS.json`

---

#### `split_runner_id.py` – Split Runner ID JSON

```bash
python3 split_runner_id.py <runner_id_file> <interval>
```

- `<runner_id_file>`: Path to the JSON file with all runner IDs.
- `<interval>`: Number of IDs per split file.

- Example:

```bash
python3 split_runner_id.py ../../frontend/public/data/raw_runner_id_data/runner_id_20250403153000.json 10000
```

- Output:
  - Creates `runner_id_YYYYMMDDHHMMSS.1.json`, `runner_id_YYYYMMDDHHMMSS.2.json`, etc.

---

#### `runner_scraper.py` – Scrape Runner Profiles

```bash
python3 runner_scraper.py <runner_id_file>
```

- `<runner_id_file>`: A split JSON file from `split_runner_id.py`.

- Example:

```bash
python3 runner_scraper.py ../../frontend/public/data/raw_runner_id_data/runner_id_20250403153000.1.json
```

- Output:
  - Saves runner profiles to `../../frontend/public/data/raw_runner_data/`.

---

#### `race_scraper.py` – Scrape Races Details

```bash
python3 race_scraper.py --min_race_uid 1 --max_race_uid 1000
```

- Optional arguments:

```bash
race_scraper.py [-h] [--min_race_uid MIN_RACE_UID]
                [--max_race_uid MAX_RACE_UID] [--year_start YEAR_START]
                [--year_end YEAR_END]
```

- Extracts race data from `https://utmb.world/utmb-index/races/{id}..{year}?page={number}`.
- `id` ranges from `<min_race_uid>` to `<max_race_uid>`, and `year` ranges from `<year_start>` to `<year_end>`.
- Default values: 1 to 100000 from 2003 to current year.

- Output:
  - Saves to `../../frontend/public/data/raw_race_data/race_<min_race_uid>_<max_race_uid>_<year_start>_<year_end>.json`

---

### 4. Data Cleaning Script

```bash
python3 clean.py
```

- Cleans JSON data by:
  - Removing duplicates.
  - Merging partial files.
  - Sorting runners by performance.
  - Saving cleaned JSON to:
    - `frontend/public/data/cleaned_runner_id.json`
    - `frontend/public/data/cleaned_runner.json`
    - `frontend/public/data/cleaned_race.json`
  - Automatically removes data inside the raw folders to save disk space.

---

### 5. Automating the Workflow

To run scraping and clean all at once:

```bash
./scrape_all_races.sh
./scrape_all_runners.sh
python3 clean.py
```

This will:

- Scrape runner IDs and split them into chunks.
- Run the scraper on each chunk.
- Scrape race data from UID 1–100000 and years up to the current year.
- Back up cleaned JSON and clear old ones.

---

### 6. Configuration Parameters

| Parameter            | Description                                                        |
| -------------------- | ------------------------------------------------------------------ |
| `DATA_DIR`           | Directory where scraped data is stored.                            |
| `CHROME_DRIVER_PATH` | Path to the Chrome WebDriver (typically in the working directory). |

---

## 7. Docker Containerization

Run the scraper using Docker for better isolation and reproducibility.

### Step 1: Build Docker Images

From the root of the project (where `docker-compose.yml` is located), run:

```bash
docker-compose build
```

This will build all necessary images, including the scraper.

### Step 2: Run Scraper Scripts

To run the `runner_id_scraper.py` (with automatic resume on crash):

```bash
docker-compose run scraper python3 webapps/backend/scraping/runner_id_scraper.py "max"
```

To run the race scraper:

```bash
docker-compose run scraper python3 webapps/backend/scraping/race_scraper.py --min_race_uid 1 --max_race_uid 100000 --year_start 2025 --year_end <current year>
```

To clean the data:

```bash
docker-compose run scraper python3 webapps/backend/scraping/clean.py
```

> You can mount `chromedriver` and the raw data directory into the container as needed.

---

## 8. Resuming Scraping

### Runner ID Scraper (`runner_id_scraper.py`)

- This script **automatically resumes** after a crash.
- If the browser crashes:
  - It saves all runner IDs collected up to that point.
  - It stores the last successfully scraped runner ID and the page number in memory.
  - It opens a new browser instance, clicks "Next" repeatedly until it finds that ID, and resumes scraping from there, assuming the runner does
  - To manually start from a particular runner Id and page, modify the initial parameter in the function
  ```
  def resume_scraping(num_pages, resume_from_runner_id=None, last_page_scraped=1):
  ```

### Race Scraper (`race_scraper.py`)

- Resume using command-line options:
  - `--min_race_uid`: Set starting race ID
  - `--year_start`: Resume from a specific year

Example:

```bash
docker-compose run scraper python3 webapps/backend/scraping/race_scraper.py --min_race_uid 88000 --year_start 2024
```

### Runner Scraper (`runner_scraper.py`)

- Resume manually by running the script on an individual chunk file:

```bash
docker-compose run scraper python3 /app/runner_scraper.py /data/cleaned_runner_id_chunk_03.json
```

---

## 9. Handling Errors and Crashes

### Sleep Mode and Browser Crashes

- Use `caffeinate` on macOS to prevent sleep during long runs:

```bash
caffeinate -i python3 runner_scraper.py ...
```

### Corrupt JSON Files

- Use tools like `jq`, `vi`, or `nano` to inspect.
- If unrecoverable, delete and rerun that segment.

---

## 10. Updating the Data

To update just the current year's race results:

```bash
rm webapps/frontend/public/data/raw_race_data/*
cp -p webapps/frontend/public/data/cleaned_race.json webapps/frontend/public/data/raw_race_data/

python3 webapps/backend/scraping/race_scraper.py --min_race_uid 1 --max_race_uid 100000 --year_start 2025 --year_end <current year>
python3 webapps/backend/scraping/clean.py
```

---

## 11. Scheduled Maintenance Scripts

### Cron Scripts

A script named `cron.sh` handles scheduled tasks like:

- Backup
- Cleanup
- Raw data folder maintenance
- Data cleaning

Located in `webapps/backend/scraping/`.

### Cron Jobs Definition

The `cronjob.txt` file defines the scraping schedule:

- Monthly runner data scraping
- Biannual runner ID scraping
- Weekly race scraping
- Weekly cleanup

---

## 12. Common Docker Usage

Run cleanup script inside the scraper container:

```bash
docker-compose run scraper bash /app/cron.sh
```

Run individual scripts:

```bash
docker-compose run scraper python3 /app/runner_scraper.py /data/cleaned_runner_id.json
docker-compose run scraper python3 /app/runner_id_scraper.py
docker-compose run scraper bash /app/scrape_races_cron.sh
```

Run full weekly pipeline:

```bash
docker-compose run scraper bash /app/cleanup_and_clean.sh
```

To avoid orphan containers:

```bash
docker-compose run --remove-orphans ...
```

## To-Do List

- Data Analysis: Identifies race trends and performance factors.
- Machine Learning: Predicts race outcomes & recommends races based on runner profiles.
- Data Visualisation: Displays charts & insights for better decision-making.
- Race Difficulty Prediction Model
- Coach-Runner Matching System
- Real-time Race Tracking
