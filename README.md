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

This project scrapes ultra-trail race and runner data using Selenium with a headless browser.

### **Race Scraper (`race_scraper.py`)**

- Extracts race data from `https://utmb.world/utmb-index/races/{id}..{year}?page={number}`.
- `id` ranges from **1 to 100000**, and `year` ranges from **2003 to 2025**.
- Uses **multiprocessing** to speed up scraping, though it may still take **days to weeks**, depending on CPU power.
- Outputs data to:
  - `webapps/frontend/public/data/raw_race_data/race.json`
- Includes details such as:
  - **City/Country**, **Date**, **Distance**, **Elevation Gain**, and race **Results**
  - Results include **Rank**, **Time** (DNF = Did Not Finish), **Name**, **Nationality** (some runners lack this), and **Age Category**
- `UTMB Index` is **not extracted** due to login restrictions.
- **Nationality Extraction:**
  - Nationality is encoded in a CSS class like `fi-{XX}`, where `XX` is a **two-letter country code** (requires post-processing).

---

### **Runner Scraper (`runner_scraper.py`)**

- Extracts all runners from the **[Runner Search Page](https://utmb.world/utmb-index/runner-search/)**.
- There are currently **230,000+ pages**, each listing **14 runners**, making this a **long-running process**.
- Uses **incremental JSON updates** to prevent crashes, allowing resumption from the last scraped `runner_id`.
- Outputs data to:
  - **Runner IDs:** `webapps/frontend/public/data/raw_runner_id_data/runner_id.json`
  - **Runner Profiles:** `webapps/frontend/public/data/raw_runner_data/runner.json`

---

### ** Configuration Parameters**

Customise these values in the script for different scraping needs:

| Parameter                                                   | Description                                                                                                                                                   |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MAXIMUM_RETRY`                                             | Retries fetching a page **every 2 seconds** if a `503 Service Temporarily Unavailable` error occurs (usually recovers in ~5 retries).                         |
| `MIN_RACE_UID`, `MAX_RACE_UID`                              | Defines the **UTMB Race ID range** (usually ≤100000).                                                                                                         |
| `YEAR_START`, `YEAR_END`                                    | Filters races by year.                                                                                                                                        |
| `TOP_N_RUNNERS`                                             | Number of runners to extract, starting from the **highest UTMB Index**.                                                                                       |
| `DATA_DIR`                                                  | Directory where scraped data is stored.                                                                                                                       |
| `RACE_JSON_PATH`, `RUNNER_JSON_PATH`, `RUNNER_ID_JSON_PATH` | Paths for race, runner, and runner ID JSON files.                                                                                                             |
| `CHROME_DRIVER_PATH`                                        | Path to the Chrome WebDriver (typically in the working directory).                                                                                            |
| `NUM_WORKERS`                                               | Number of parallel processes for multiprocessing.                                                                                                             |
| `SAVE_RUNNER_ID_EVERY_PAGES`                                | Interval (in pages) for saving **runner IDs** to JSON.                                                                                                        |
| `SAVE_RUNNER_DATA_EVERY`                                    | Interval (in profiles) for saving **runner data** to JSON.                                                                                                    |
| `SAVE_RACE_DATA_EVERY`                                      | Interval (in races) for saving **race data** to JSON.                                                                                                         |
| `UPDATE_RUNNER_PROFILE_ONLY`                                | If `True`, extracts only **runner profiles** from `RUNNER_ID_JSON_PATH` without re-scraping IDs.                                                              |
| `CHECK_DUPLICATE`                                           | If `False`, fetch all available race data without checking if it exists in the json file already will reduce computational time for creating a new json file. |

---

### ** Important Notes**

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
  - Modify `RUNNER_ID_JSON_PATH` to remove already-scraped IDs.
  - Use `cp -p runner_id.json temp.json` to create a backup, then **remove completed runners**.
  - Set `UPDATE_RUNNER_PROFILE_ONLY = False` to **re-extract missing profiles**.

# Data Cleaning Script

This script cleans JSON data files by removing duplicate keys in dictionaries and duplicate values in arrays.

## Features

- Concatenate a list of json for `race.json`, `runner.json`, `runner_id.json` inside their raw data folders respectively.
- Removes duplicate keys in `race.json` and `runner.json`, keeping only the last occurrence.
- Removes duplicate values in `runner_id.json`.
- Ranks runners by:
  - **General UTMB Index** (higher value is better).
  - **Total of 20K, 50K, 100K, and 100M UTMB Index values** (higher total is better).
- Saves cleaned data to new files with `cleaned_` prefix.

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
