import json
import sys
import os
import multiprocessing
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException


# Configuration
BASE_URL = "https://utmb.world/utmb-index/runner-search"
DATA_DIR = "../../frontend/public/data"
RUNNER_JSON_PATH = os.path.join(DATA_DIR, "raw_runner",f'runner_{datetime.datetime.now():%Y%m%d%H%M%S}.json')
CHROME_DRIVER_PATH = "./chromedriver"
MAX_RETRIES = 100  # Maximum retry attempts for 503 errors
NUM_PROCESSES = 20  # Number of parallel processes for runner profile scraping


def setup_browser():
    """Set up a headless Chrome browser for scraping."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=chrome_options)


def save_data(file_path, data):
    """Save data to a JSON file."""
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def get_page_with_retries(driver, url, max_retries=MAX_RETRIES):
    """Attempt to load a webpage multiple times in case of 503 errors."""
    for attempt in range(1, max_retries + 1):
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            if "503 Service Temporarily Unavailable" in driver.page_source:
                raise WebDriverException("503 Service Unavailable")
            return True  # Successfully loaded
        except (TimeoutException, WebDriverException) as e:
            print(f"[Retry {attempt}/{max_retries}] Failed to load {url}: {e}")
    print(f"Error: Unable to load {url} after {max_retries} retries.")
    return False  # Failed after max retries


def scrape_runner_profile(runner_id):
    """Scrape profile data for a given runner ID."""
    driver = setup_browser()
    runner_url = f"https://utmb.world/en/runner/{runner_id}"

    if not get_page_with_retries(driver, runner_url):
        driver.quit()
        return None

    soup = BeautifulSoup(driver.page_source, "html.parser")

    name = soup.select_one("h1").text.strip() if soup.select_one("h1") else None
    age_group = None
    nationality = None

    age_element = soup.find("p", string="Age")
    if age_element:
        age_group = age_element.find_next("span").text.strip()

    nationality_element = soup.find("p", string="Nationality")
    if nationality_element:
        nationality = nationality_element.find_next("span").text.strip()

    # Extract UTMB Index
    utmb_indexes = {}
    index_labels = ["General", "20K", "50K", "100K", "100M"]
    index_values = soup.select(".performance_stat__hcZM_")
    for label, value in zip(index_labels, index_values):
        utmb_indexes[label] = value.text.strip() if value else None

    # Extract club and sponsor details
    club, sponsor = None, None
    details = soup.select(".runner-more-details_details_element__3rIxF")
    for detail in details:
        title_element = detail.select_one(".runner-more-details_details_title__RIv1N")
        content_element = detail.select_one(".runner-more-details_details_content__ZiSil")
        if title_element and content_element:
            title = title_element.text.strip()
            content = content_element.text.strip()
            if title == "Club":
                club = content
            elif title == "Sponsor(s)":
                sponsor = content

    driver.quit()
    print(f"Scraped runner: {runner_id}")

    # Return only non-empty fields
    return {
        key: value
        for key, value in {
            "id": runner_id,
            "name": name,
            "age_group": age_group,
            "nationality": nationality,
            "UTMB Index": utmb_indexes,
            "club": club,
            "sponsor": sponsor,
        }.items()
        if value
    }


def scrape_runners(runner_ids):
    """Scrape multiple runner profiles using multiprocessing."""
    runners_data = []
    scraped_count = 0

    with multiprocessing.Pool(NUM_PROCESSES) as pool:
        for result in pool.imap(scrape_runner_profile, runner_ids):
            if result:
                runners_data.append(result)
                scraped_count += 1


    save_data(RUNNER_JSON_PATH, runners_data)
    print(f"Scraping completed. Total runners scraped: {len(runner_ids)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 runner_scraper.py <path_to_runner_ids_json>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    try:
        with open(file_path, "r") as f:
            runner_ids = json.load(f)
            scrape_runners(runner_ids)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file - {e}")
        sys.exit(1)
