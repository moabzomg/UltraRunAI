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

## To-Do List

- Web Scraping: Collects ultra-trail race and runner data using Selenium with headless browser.
  - `Race_scraper.py` extracts all races using the url https://utmb.world/utmb-index/races/{id}..{year}?page={number}, where `id` ranges from 1 to 100000, `year` ranges from 2003 to 2025, using loops with multiprocessing technique to save computational time, which may takes several days to weeks, depending your CPU. The result will output to `webapps/frontend/public/data/race.json` with information including `City/Country`, `Date`, `Distance`, `Elevation Gain` and a list of `Results` with `Rank`, `Time` (**DNF** means did not finish the race), `Name`, `Nationality` (There are some runners do not have nationality) and `Age Category`. `UTMB Index` is not extracted since login is required.
  - `Runner_scraper.py` extracts all runners in the page [Runner Search](https://utmb.world/utmb-index/runner-search/), by finding all runner IDs in the available pages. At the moment, there are more than 230000 pages with each page 14 runners, you can imagine the runtime of the python program. Therefore, json is updated at intervals to prevent crashes, so that we can continue scraping from the last scraped runner_id or runner profile. The list of runner IDs json will output to `webapps/frontend/public/data/runner_id.json` and the runner profile json will output to `webapps/frontend/public/data/runner.json`, with all available information. For the nationality, we can extract it with the class name, which is fi-{XX}, represented by 2 alphabets, which required further processing.
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
