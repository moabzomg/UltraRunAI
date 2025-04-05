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

### 7. Docker Containerization

Run the scraper using Docker for better isolation and reproducibility.

#### Step 1: Build the Docker images

From the root of the project (where `docker-compose.yml` is located), run:

```bash
docker-compose build
```

This will build all the necessary images, including the scraper.

#### Step 2: Run any scraper

The easiest way to run the scraper is via Docker Compose. Docker Compose will manage dependencies and the execution environment for you.

To run the scraper (e.g., `runner_id_scraper.py`), use the following command:

```bash
docker-compose run scraper python3 webapps/backend/scraping/runner_id_scraper.py "max"
```

To run `clean.py`:

```bash
docker-compose run scraper python3 webapps/backend/scraping/clean.py
```

> You can mount ChromeDriver and the raw data directory into the container as needed.

---

### 8. Notes

#### 💤 Sleep Mode & Crashes

- `race_scraper.py` resumes automatically after interruption.
- `runner_scraper.py` should be restarted manually with the appropriate chunk.

#### ⚠️ Corrupt JSON Files

- Use `vi`, `nano`, or `jq` to inspect and fix.
- If unrecoverable, delete and rerun that segment.

#### 🔁 Resuming Scraping

- Use `--min_race_uid` and `--year_start` to resume `race_scraper.py`.
- Rerun individual split files with `runner_scraper.py`.

---

### 9. Updating the Data

To update just the current year's race results:

```bash
rm webapps/frontend/public/data/raw_race_data/*
cp -p webapps/frontend/public/data/cleaned_race.json webapps/frontend/public/data/raw_race_data/
python3 race_scraper.py --min_race_uid 1 --max_race_uid 100000 --year_start 2025 --year_end <current year>
python3 clean.py
```

---

### 10. Runtime and Optimisation

- `race_scraper.py` uses multiprocessing for speed.
- Runner data is chunked to reduce memory usage and risk of crash.
- Keep your Mac awake during scraping using:

```bash
caffeinate -i python3 runner_scraper.py ...
```

---

### 11. Scheduled Cleanup Script

The `cron.sh` script performs backup, runs the cleaner, and manages raw data folders. It is intended to be run automatically as part of the scheduled maintenance tasks.

#### Cron Jobs

The `cronjob.txt` file defines the scraping schedule, including:

- Monthly runner data scraping
- Biannual runner ID scraping
- Weekly race scraping
- Weekly cleanup and data processing

Both files are located in `backend/scraping/`.

#### Docker Usage

To run the cleanup script inside the `scraper` container:

```bash
docker-compose run scraper bash /app/cron.sh
```

To test individual scraper scripts:

```bash
docker-compose run scraper python3 /app/runner_scraper.py /data/cleaned_runner_id.json
docker-compose run scraper python3 /app/runner_id_scraper.py
docker-compose run scraper bash /app/scrape_races_cron.sh
```

To execute the full weekly cleanup and clean-up logic:

```bash
docker-compose run scraper bash /app/cleanup_and_clean.sh
```

To avoid orphan containers, you can add:

```bash
--remove-orphans
```

to your `docker-compose` commands.

## To-Do List

- Data Analysis: Identifies race trends and performance factors.
- Machine Learning: Predicts race outcomes & recommends races based on runner profiles.
- Data Visualisation: Displays charts & insights for better decision-making.
- Race Difficulty Prediction Model
- Coach-Runner Matching System
- Real-time Race Tracking

## How to Use

### Backend

```

pip3 install -r requirements.txt
python3 app.py

```

, the script will set up the environment and start the Flask server to start the backend.

### Frontend

To display the React page in [localhost](http://localhost:3000/), simply execute

```

npm install
npm run start

```

```

```
