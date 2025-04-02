import json
import os
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from bs4 import BeautifulSoup

# Configuration
BASE_URL = "https://utmb.world/utmb-index/runner-search"
DATA_DIR = "../../frontend/public/data/"
RUNNER_JSON_PATH = os.path.join(DATA_DIR, "runner.json")
RUNNER_ID_JSON_PATH = os.path.join(DATA_DIR, "runner_id.json")
CHROME_DRIVER_PATH = "./chromedriver"
TOP_N_RUNNERS = 1000000  # Number of runners to scrape
MAX_RETRIES = 100  # Maximum retry attempts for 503 errors
SAVE_RUNNER_ID_EVERY_PAGES = 20
SAVE_RUNNER_DATA_EVERY = 10
NUM_PROCESSES = 4  # Number of parallel processes for runner profile scraping
UPDATE_RUNNER_PROFILE_ONLY = True

def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=chrome_options)

def load_existing_data(file_path, default=None):
    """Load existing JSON data if the file exists."""
    if default is None:
        default = []
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r") as file:
            return json.load(file)
    return default

def save_data(file_path, data):
    """Save data to JSON file."""
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def get_page_with_retries(driver, url, max_retries=MAX_RETRIES):
    """Retry loading a webpage in case of 503 errors."""
    attempt = 0
    while attempt < max_retries:
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            if "503 Service Temporarily Unavailable" in driver.page_source:
                raise WebDriverException("503 Service Unavailable")
            return True  # Page loaded successfully
        except (TimeoutException, WebDriverException) as e:
            print(f"Attempt {attempt + 1}: Error loading {url} - {e}")
            attempt += 1
    print(f"Failed to load {url} after {max_retries} retries.")
    return False  # Failed after max retries

def get_max_pages(driver):
    """Dynamically find the maximum number of pages available."""
    max_pages = 1  # Default
    try:
        driver.get(BASE_URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find the last pagination number
        page_numbers = [int(link.text) for link in soup.select(".pagination_paginate_link__c9A6i") if link.text.isdigit()]
        if page_numbers:
            max_pages = max(page_numbers)
    except WebDriverException as e:
        print(f"Error finding max pages: {e}")

    print(f"Max pages found: {max_pages}")
    return max_pages

def extract_runner_ids(driver):
    """Extract runner IDs from the current page."""
    soup = BeautifulSoup(driver.page_source, "html.parser")
    runner_rows = soup.select(".my-table_row__nlm_j")
    runner_ids = []
    for row in runner_rows:
        link_elem = row.select_one("a[href*='/en/runner/']")
        if link_elem:
            runner_id = link_elem["href"].split("/")[-1]
            runner_ids.append(runner_id)
    return runner_ids

def scrape_runner_ids(all_runner_ids):
    driver = setup_browser()
    if not get_page_with_retries(driver, BASE_URL):
        driver.quit()
        return
    new_runner_ids = set()

    max_pages = get_max_pages(driver)
    current_page = 1

    while current_page <=max_pages:
        print(f"Scraping Page {current_page}/{max_pages}")

        # Wait until the current page is active
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"a[aria-label='Page {current_page} is your current page']"))
        )

        runner_ids = extract_runner_ids(driver)
        new_runner_ids.update(set(runner_ids) - all_runner_ids)
        all_runner_ids.update(runner_ids)

        print(f"Found {len(set(runner_ids) - all_runner_ids)} new runners on page {current_page}")

        if current_page % SAVE_RUNNER_ID_EVERY_PAGES == 0:
            save_data(RUNNER_ID_JSON_PATH, list(all_runner_ids))
            print(f"Saved runner IDs ({len(all_runner_ids)})")

        # Click 'Next' if available
        next_button = driver.find_elements(By.CSS_SELECTOR, "a[rel='next']")
        if next_button:
            if next_button[0].get_attribute("aria-disabled") != "true":
                driver.execute_script("arguments[0].click();", next_button[0])
            else:
                print("No more pages to scrape.")
                break
        else:
            print("Next button not found.")
            break

        current_page += 1

    driver.quit()
    save_data(RUNNER_ID_JSON_PATH, list(all_runner_ids))

def scrape_runner_profile(runner_id):
    driver = setup_browser()
    runner_url = f"https://utmb.world/en/runner/{runner_id}"
    if not get_page_with_retries(driver, runner_url):
        driver.quit()
        return None

    soup = BeautifulSoup(driver.page_source, "html.parser")
    name = soup.select_one("h1").text.strip()
    age_element = soup.find("p", string="Age")
    age_group = age_element.find_next("span").text.strip() if age_element else None
    nationality_element = soup.find("p", string="Nationality")
    nationality = nationality_element.find_next("span").text.strip() if nationality_element else None

    utmb_indexes = {}
    index_labels = ["General", "20K", "50K", "100K", "100M"]
    index_values = soup.select(".performance_stat__hcZM_")
    for label, value in zip(index_labels, index_values):
        utmb_indexes[label] = value.text.strip() if value else None

    club, sponsor = None, None
    details = soup.select(".runner-more-details_details_element__3rIxF")
    for detail in details:
        title_element = detail.select_one(".runner-more-details_details_title__RIv1N")
        if title_element:
            title = title_element.text.strip()
        content_element = detail.select_one(".runner-more-details_details_content__ZiSil")
        if content_element:
            content = content_element.text.strip()
        if title == "Club":
            club = content
        elif title == "Sponsor(s)":
            sponsor = content
            
    

    driver.quit()
    print (f'Scraped {runner_id}')
    return {
        key: value for key, value in {                  
            "id": runner_id,
            "name": name,
            "age_group": age_group,
            "nationality": nationality,
            "UTMB Index": utmb_indexes,
            "club": club,
            "sponsor": sponsor,
        }.items() if value
    }
    
def scrape_runners():
    

    existing_runner_ids = set(load_existing_data(RUNNER_ID_JSON_PATH, default=[]))
    all_runner_ids = set(existing_runner_ids)
    if not UPDATE_RUNNER_PROFILE_ONLY:
        with multiprocessing.Pool(NUM_PROCESSES) as pool:
            scrape_runner_ids(all_runner_ids)
    # Scrape runner profiles using multiprocessing
    runners_data = load_existing_data(RUNNER_JSON_PATH)
    runners = list(all_runner_ids)
    batch_size = SAVE_RUNNER_DATA_EVERY
    scraped_count = 0

    with multiprocessing.Pool(NUM_PROCESSES) as pool:
        for result in pool.imap(scrape_runner_profile, runners):
            if result:
                runners_data.append(result)
                scraped_count += 1

            # Save every `SAVE_RUNNER_DATA_EVERY` runners
            if scraped_count % batch_size == 0:
                save_data(RUNNER_JSON_PATH, runners_data)
                print(f"Saved runner data ({len(runners_data)} entries out of {len(runners)})")
                
    save_data(RUNNER_JSON_PATH, runners_data)
    print(f"Scraped {len(runners)} runners. Total: {len(runners_data)}")

if __name__ == "__main__":
    scrape_runners()
