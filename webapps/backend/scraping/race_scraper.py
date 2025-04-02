import requests
from pathlib import Path
import json
from bs4 import BeautifulSoup
from multiprocessing import Pool, Manager, cpu_count

# Parameters
MIN_RACE_UID = 2759
MAX_RACE_UID = 100000
YEAR_START = 2003
YEAR_END = 2025
RACE_JSON_PATH = "../../frontend/public/data/raw_race_data/race.json"
NUM_PROCESSES = 4
SAVE_RACE_DATA_EVERY = 500
CHECK_DUPLICATE = False


def get_meta_info(response):
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Initialise default values
    city_country = None
    date = None
    distance = None
    elevation_gain = None

    # Extract City/Country
    city_country_elem = soup.find("p", string="City / Country")
    if city_country_elem:
        city_country = city_country_elem.find_next("p").text.strip()

    # Extract Date
    date_elem = soup.find("p", string="Date")
    if date_elem:
        date = date_elem.find_next("span").text.strip()

    # Extract Distance
    distance_elem = soup.find("p", string="Distance")
    if distance_elem:
        distance = distance_elem.find_next("span").text.strip()

    # Extract Elevation Gain
    elevation_gain_elem = soup.find("p", string="Elevation Gain")
    if elevation_gain_elem:
        elevation_gain = elevation_gain_elem.find_next("span").text.strip()

    return {
        "City/Country": city_country,
        "Date": date,
        "Distance": distance,
        "Elevation Gain": elevation_gain,
        "Results": []
    }


def extract_race_results(soup, info):
    rows = soup.find_all("div", class_="my-table_row__nlm_j")
    
    for row in rows:
        cols = row.find_all("div", class_="my-table_cell__z__zN")
        if len(cols) < 6:  # Ensure the row has enough columns
            continue

        rank = cols[0].text.strip()
        time = cols[1].text.strip()
        name = cols[2].find("a").text.strip()
        runner_link = cols[2].find("a")["href"] if cols[2].find("a") else None
        runner_id = runner_link.split("/")[-1] if runner_link else None
        nationality = cols[3].text.strip().split()[-1] if cols[3].text.strip().split() else None
        age_category = cols[5].text.strip()

        if rank == "DNF":
            info["Results"].append({"Name": name, "Time": "DNF", "Nationality": nationality, "Age": age_category})
        else:
            info["Results"].append({
                "Rank": int(rank),
                "Time": time,
                "Name": name,
                "Id": runner_id,
                "Nationality": nationality,
                "Age": age_category,
            })


def fetch_race_data(race_uid, year):
    """Fetch and parse race data."""
    url = f'https://utmb.world/utmb-index/races/{race_uid}..{year}'
    response = requests.get(url)

    if response.status_code == 404:
        return None  # No race found
    
    print(f'race {race_uid} in {year} found')

    soup = BeautifulSoup(response.content, "html.parser")

    # Extract race info on first page
    info = get_meta_info(response)
    if not all([info["City/Country"], info["Date"], info["Distance"], info["Elevation Gain"]]):
        return None  # Return None if essential elements are missing

    extract_race_results(soup, info)

    return info if info["Results"] else None  # Only return if results exist


def process_race_task(args):
    race_uid, year, existing_results = args
    utmb_key = f"{race_uid}.{year}"
    if CHECK_DUPLICATE:
        if utmb_key in existing_results:
            return utmb_key, None  # Skip already processed races

    race_data = fetch_race_data(race_uid, year)
    return utmb_key, race_data


def save_progress(utmb_results):
    with open(RACE_JSON_PATH, 'w') as f:
        json.dump(utmb_results, f, indent=4)


def scrape_races_parallel():
    # Load previous results
    if Path(RACE_JSON_PATH).exists() and Path(RACE_JSON_PATH).stat().st_size > 0:
        with open(RACE_JSON_PATH, "r") as f:
            utmb_results = json.load(f)
    else:
        utmb_results = {}

    # Prepare task list
    tasks = [(race_uid, year, utmb_results) for race_uid in range(MIN_RACE_UID,MAX_RACE_UID) for year in range(YEAR_START, YEAR_END)]
    
    with Pool(NUM_PROCESSES) as pool:
        for i, (utmb_key, race_data) in enumerate(pool.imap_unordered(process_race_task, tasks)):
            if race_data:
                utmb_results[utmb_key] = race_data

            if i % SAVE_RACE_DATA_EVERY == 0:         
                save_progress(utmb_results)
                print("JSON Saved")

    # Final save
    save_progress(utmb_results)


if __name__ == "__main__":
    scrape_races_parallel()
