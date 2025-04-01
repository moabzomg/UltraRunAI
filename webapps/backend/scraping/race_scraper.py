import requests
from tqdm import tqdm
from pathlib import Path
import json
from bs4 import BeautifulSoup

# Parameters
MAX_RACE_UID = 100000
YEAR_START = 2003
YEAR_END = 2025
RACE_JSON_PATH = "../../frontend/public/data/race.json"

def get_meta_info(response):
    """Extract race metadata including City/Country, Date, Distance, Elevation Gain, and Race Category."""
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Initialize default values
    city_country = None
    date = None
    distance = None
    elevation_gain = None
    race_category = None

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


    # Return extracted information
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
        
        rank = cols[0].text.strip()
        time = cols[1].text.strip()
        name = cols[2].find("a").text.strip()
        nationality = cols[3].text.strip().split()[-1]  # Extracts country name
        age_category = cols[5].text.strip()

        # Skip DNF (Did Not Finish)
        if rank == "DNF":
            info["Results"].append({"Name": name, "Time": "DNF", "Nationality": nationality, "Age": age_category})
        else:
            info["Results"].append({
                "Rank": int(rank),
                "Time": time,
                "Name": name,
                "Nationality": nationality,
                "Age": age_category,
            })

def fetch_race_data(race_uid, year):
    """Fetch and parse race data."""
    url = f'https://utmb.world/utmb-index/races/{race_uid}..{year}'
    response = requests.get(url)
    if response.status_code == 404:
        return None  # No race found

    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extract race info on first page
    info = get_meta_info(response)
    if not all([info["City/Country"], info["Date"], info["Distance"], info["Elevation Gain"]]):
        return None  # Return None if any of the essential elements are missing
    
    extract_race_results(soup, info)

    return info if info["Results"] else None  # Only return if results exist

# Load previous results
if Path(RACE_JSON_PATH).exists() and Path(RACE_JSON_PATH).stat().st_size > 0:
    with open(RACE_JSON_PATH, "r") as f:
        utmb_results = json.load(f)
else:
    utmb_results = {}

# Fetch race data
for race_uid in tqdm(range(MAX_RACE_UID)):
    for year in range(YEAR_START, YEAR_END):
        utmb_key = f"{race_uid}.{year}"
        if utmb_key in utmb_results:
            continue  # Skip already processed races

        race_data = fetch_race_data(race_uid, year)
        if race_data:
            utmb_results[utmb_key] = race_data

        # Save results every 20 races
        if len(utmb_results) % 20 == 0:
            with open(RACE_JSON_PATH, 'w') as f:
                json.dump(utmb_results, f, indent=4)

# Final save
with open(RACE_JSON_PATH, 'w') as f:
    json.dump(utmb_results, f, indent=4)
