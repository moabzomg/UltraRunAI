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

### Race Scraper

4. **`race_scraper.py`**
   - Scrapes **UTMB race results** from a given range of race UIDs and years.
   - Saves race results in **JSON format**.

---

### 2. Usage Instructions

Run the Full Scraping Process for 3M+ runners incrementally

```
cd webapps/backend/scraping
./scrape_all_runners.sh
```

Run the Full Scraping Process for 40000+ races incrementally

```
cd webapps/backend/scraping
./scrape_all_races.sh
```

### 3.Script-Specific Usage

- runner_id_scraper.py - Extracts all runners IDs from the **[Runner Search Page](https://utmb.world/utmb-index/runner-search/)**. There are currently **230,000+ pages**, each listing **14 runners**, making this a **long-running process**.

```
python3 runner_id_scraper.py <NUM_PAGES>
```

    - `<NUM_PAGES>`: Number of pages to scrape (use `"max"` for all pages).
    - Example: Scrape all pages:
    ```
    python3 runner_id_scraper.py "max"
    ```
    - Output:
      - Saves runner IDs to `../../frontend/public/data/raw_runner_id/runner_id_YYYYMMDDHHMMSS.json`

- split_runner_id.py - Split Runner ID JSON

```
python3 split_runner_id.py <runner_id_file> <interval>
```

    - `<runner_id_file>`: Path to the JSON file with all runner IDs.

    - `<interval>`: Number of IDs per split file.

    - Example: Split into 10,000-runner chunks:
    ```
    python3 split_runner_id.py ../../frontend/public/data/raw_runner_id/runner_id_20250403153000.json 10000 ```
    ```
    - Output:
      - Creates `runner_id_YYYYMMDDHHMMSS.1.json`, `runner_id_YYYYMMDDHHMMSS.2.json`, etc.

- runner_scraper.py - Scrape Runner Profiles

```
python3 runner_scraper.py <runner_id_file>
```

    - `<runner_id_file>`: A split JSON file from `split_runner_id.py`.
    - Example:
    ```
    python3 runner_scraper.py ../../frontend/public/data/raw_runner_id/runner_id_20250403153000.1.json
    ```
    - Output:
      - Saves runner profiles to `../../frontend/public/data/raw_runner_data/`.

- race_scraper.py - Scrape Races details
  - Extracts race data from `https://utmb.world/utmb-index/races/{id}..{year}?page={number}`.
  - `id` ranges from `<min_race_uid>` to `<max_race_uid> `, and `year` ranges from `<year_start>` to `<year_end>`, with defaults 1, 100000, 2003 and current year respectively.
  - Uses **multiprocessing** to speed up scraping, though it may still take **days to weeks**, depending on CPU power.
  - Outputs data to:
    - `webapps/frontend/public/data/raw_race_data/`
  - Includes details such as:
    - **City/Country**, **Date**, **Distance**, **Elevation Gain**, and race **Results**
    - Results include **Rank**, **Time** (DNF = Did Not Finish), **Name**, **Nationality** (some runners lack this), and **Age Category**
  - `UTMB Index` is **not extracted** due to login restrictions.
  - **Nationality Extraction:**
    - Nationality is encoded in a CSS class like `fi-{XX}`, where `XX` is a **two-letter country code** (requires post-processing).
  - `argparse` is used for parsing arguments. run
  ```
  python3 race_scraper.py --help
  ```
  for detail usage:
  ```race_scraper.py [-h] [--min_race_uid MIN_RACE_UID]
                     [--max_race_uid MAX_RACE_UID] [--year_start YEAR_START]
                     [--year_end YEAR_END]
  ```
  - Example:
  ````
  python3 race_scraper.py --min_race_uid 1 --max_race_uid 1000 ```
  - Output:
    - Saves runner profiles to `../../frontend/public/data/raw_race_data/race_<min_race_uid>_<max_race_uid>_<year_start>_<year_end>.json`.
  ````

### Data Cleaning Script

Scrape incrementally for race ID and runner ID respectively and output to several files could significantly reduce computational time. By executing `clean.py`, the json files will be concatenated and output to `webapps/frontend/public/data/raw_race_data/`

This script cleans JSON data files by removing duplicate keys in dictionaries and duplicate values in arrays.

#### Features

- Concatenate a list of json for race, runner and runner_id inside their raw data folders respectively.
- Removes duplicate keys for race and runner, keeping only the last occurrence.
- Removes duplicate values for runner_id.
- Ranks runners by:
  - **General UTMB Index** (higher value is better).
  - **Total of 20K, 50K, 100K, and 100M UTMB Index values** (higher total is better).
- Saves cleaned data to new files with `cleaned_` prefix.
- Remove all data in raw data folders and replaced by the cleaned data

### 4. Automating the Workflow

To scrape everything at once with efficiency by incremental extraction, run the shell script:

```
./scrape_all_races.sh
./scrape_all_runners.sh
./clean.py
```

#### What It Does

Scraping process may take a long time up to weeks, do it incrementally and

- Race Scraper

  - Scrapes all races UID from 1 to 100000 by splitting into a interval of 5000 and output to the json file, from the year of 2003 to 2025

- Runner Scraper

  - Scrapes all runner IDs (runner_id_scraper.py max).

  - Finds the latest runner_id JSON file.

  - Splits it into 10,000-runner chunks (split_runner_id.py).

  - Runs runner_scraper.py for each chunk.

- Clean
  - Concatenate json and output `cleaned_runner_id.json`, `cleaned_runner.json` and `cleaned_race.json` to `webapps/frontend/public/data/` and remove duplicates.

---

### ** Configuration Parameters**

Customise these values in the script for different scraping needs:

| Parameter            | Description                                                                                                                           |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `MAXIMUM_RETRY`      | Retries fetching a page **every 2 seconds** if a `503 Service Temporarily Unavailable` error occurs (usually recovers in ~5 retries). |
| `DATA_DIR`           | Directory where scraped data is stored.                                                                                               |
| `CHROME_DRIVER_PATH` | Path to the Chrome WebDriver (typically in the working directory).                                                                    |

---

### ** Notes**

**Handling Sleep Mode & Crashes:**

- `race_scraper.py` **automatically resumes** if the computer sleeps and wakes up.
- `runner_scraper.py` **does NOT resume** because the **headless browser terminates** upon sleep.

  **Recovering from Corrupt JSON Files:**

- If a JSON file **fails to load**, it may be corrupted.
- Open the JSON with `vi`, append new data manually (`Shift + G` to go to the end), and **fix syntax errors**.
- If necessary, **empty the file** and start fresh.

  **Resuming Scraping Manually:**

- **For `race_scraper.py`**:
  - Set `MIN_RACE_UID` to the last extracted **race ID** before the crash.
- **For `runner_scraper.py`**:
  - Run with parameters `<runner_id_file>` for the json files to be extracted.

### Update Data

- Assuming historical data will not change for past races, update races by running

```
  rm webapps/frontend/public/data/raw_race_data/*
  cp -p webapps/frontend/public/data/cleaned_race_data.json webapps/frontend/public/data/raw_race_data/
  python3 race_scraper.py --min_race_uid 1 --max_race_uid 100000 --year_start 2025 --year_end <current year>
  clean.py
```

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
