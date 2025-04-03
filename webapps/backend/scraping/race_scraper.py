import os
import requests
from pathlib import Path
import json
import argparse
from bs4 import BeautifulSoup
from multiprocessing import Pool, cpu_count
import datetime

# Default parameters
DEFAULT_MIN_RACE_UID = 1
DEFAULT_MAX_RACE_UID = 100000
DEFAULT_YEAR_START = 2003
DEFAULT_YEAR_END = datetime.datetime.now().year
DATA_DIR = "../../frontend/public/data"
NUM_PROCESSES = 20


def get_meta_info(response):
    soup = BeautifulSoup(response.content, "html.parser")

    # Initialise default values
    city_country, date, distance, elevation_gain = None, None, None, None

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
        if len(cols) < 6:
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

    print(f'Race {race_uid} in {year} found')

    soup = BeautifulSoup(response.content, "html.parser")

    # Extract race info on first page
    info = get_meta_info(response)
    if not all([info["City/Country"], info["Date"], info["Distance"], info["Elevation Gain"]]):
        return None  # Return None if essential elements are missing

    extract_race_results(soup, info)

    return info if info["Results"] else None  # Only return if results exist


def process_race_task(args):
    race_uid, year = args
    utmb_key = f"{race_uid}.{year}"
    race_data = fetch_race_data(race_uid, year)
    return utmb_key, race_data


def save_progress(utmb_results, race_json_path):
    with open(race_json_path, 'w') as f:
        json.dump(utmb_results, f, indent=4)


def scrape_races(min_race_uid, max_race_uid, year_start, year_end):
    utmb_results = {}

    # Prepare task list
    tasks = [(race_uid, year) for race_uid in range(min_race_uid, max_race_uid) for year in range(year_start, year_end)]

    with Pool(NUM_PROCESSES) as pool:
        for i, (utmb_key, race_data) in enumerate(pool.imap_unordered(process_race_task, tasks)):
            if race_data:
                utmb_results[utmb_key] = race_data
    # Final save
    save_progress(utmb_results, RACE_JSON_PATH)
    print(f"JSON saved up to {utmb_key}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape UTMB race results.")
    parser.add_argument("--min_race_uid", type=int, default=DEFAULT_MIN_RACE_UID, help="Minimum race UID to start scraping. Default 1")
    parser.add_argument("--max_race_uid", type=int, default=DEFAULT_MAX_RACE_UID, help="Maximum race UID to scrape. Default 100000")
    parser.add_argument("--year_start", type=int, default=DEFAULT_YEAR_START, help="Starting year for scraping. Default 2002")
    parser.add_argument("--year_end", type=int, default=DEFAULT_YEAR_END, help="Ending year for scraping. Default current year")

    args = parser.parse_args()
    RACE_JSON_PATH = os.path.join(DATA_DIR, "raw_race", f'race_{args.min_race_uid}_{args.max_race_uid}_{args.year_start}_{args.year_end}.json')

    scrape_races(args.min_race_uid, args.max_race_uid, args.year_start, args.year_end)
