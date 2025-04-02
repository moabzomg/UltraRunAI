import json
import os
import time
import re
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
MAX_RETRIES = 100 # Maximum retry attempts for 503 errors
def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=chrome_options)
driver = setup_browser()

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

def get_page_with_retries(url, max_retries=MAX_RETRIES):
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
            time.sleep(2)  # Wait before retrying
    print(f"Failed to load {url} after {max_retries} retries.")
    return False  # Failed after max retries

def get_max_pages():
    """Dynamically find the maximum number of pages available."""
    max_pages = 1  # Default
    driver_max_page = setup_browser()
    try:
        driver_max_page.get(BASE_URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        soup = BeautifulSoup(driver_max_page.page_source, "html.parser")

        # Find the last pagination number
        page_numbers = []
        pagination_links = soup.select(".pagination_paginate_link__c9A6i[aria-label*='Page ']")
        for link in pagination_links:
            match = re.search(r"Page (\d+)", link.get("aria-label", ""))
            if match:
                page_numbers.append(int(match.group(1)))

        if page_numbers:
            max_pages = max(page_numbers)

    except WebDriverException as e:
        print(f"Error finding max pages: {e}")
    finally:
        driver_max_page.quit()

    print(f"Max pages found: {max_pages}")
    return max_pages

def extract_runner_ids():
    soup = BeautifulSoup(driver.page_source, "html.parser")
    runner_ids = []

    runner_rows = soup.select(".my-table_row__nlm_j")
    for row in runner_rows:
        link_elem = row.select_one("a[href*='/en/runner/']")
        if link_elem:
            runner_id = link_elem["href"].split("/")[-1]
            runner_ids.append(runner_id)
    return runner_ids

def scrape_runner_profiles(runner_ids):
    """Scrape runner details from their profile pages."""
    runners_data = load_existing_data(RUNNER_JSON_PATH)

    for runner_id in runner_ids:
        runner_url = f"https://utmb.world/en/runner/{runner_id}"

        if not get_page_with_retries(runner_url):
            continue  # Skip if page fails to load

        soup = BeautifulSoup(driver.page_source, "html.parser")

        try:
            # Extract basic details
            name = soup.select_one("h1").text.strip()
            age_group = soup.select_one(".runner-age-category").text.strip() if soup.select_one(".runner-age-category") else None
            nationality = soup.select_one(".runner-nationality").text.strip() if soup.select_one(".runner-nationality") else None

            # Extract UTMB Index
            utmb_indexes = {}
            index_labels = ["General", "20K", "50K", "100K", "100M"]
            index_values = soup.select(".performance_stat__hcZM_")
            for label, value in zip(index_labels, index_values):
                utmb_indexes[label] = value.text.strip() if value else None

            # Extract Club & Sponsor
            club, sponsor = None, None
            details = soup.select(".runner-more-details_details_element__3rIxF")
            for detail in details:
                title_elem = detail.select_one(".runner-more-details_details_title__RIv1N")
                content_elem = detail.select_one(".runner-more-details_details_content__ZiSil")
                if title_elem and content_elem:
                    title = title_elem.text.strip()
                    content = content_elem.text.strip()
                    if title == "Club":
                        club = content
                    elif title == "Sponsor(s)":
                        sponsor = content

            # Extract Race Details
            races = []
            race_rows = soup.select(".my-table_row__nlm_j")
            for row in race_rows:
                cols = row.select(".my-table_cell__z__zN")
                if len(cols) >= 8:
                    # Extract country
                    country_element = cols[2].select_one("span[class^='results-table_flag__']")
                    country = next((cls.split("-")[-1].upper() for cls in country_element["class"] if cls.startswith("fi-")), None)

                    # Extract race category
                    category_element = row.select_one(".pi-category-logo_container__1zLvC img")
                    category = category_element["alt"] if category_element else None

                    race_name = cols[1].text.strip()
                    year = cols[0].text.strip().split(" ")[-1]  # Extract the year

                    races.append({
                        "name": race_name,
                        "year": year,
                        "country": country,
                        "category": category,
                        "distance_elevation": cols[4].text.strip(),
                        "time": cols[5].text.strip(),
                        "rank": cols[6].text.strip(),
                        "genderscore": cols[7].text.strip(),
                    })

            # Save runner data
            runner_data = {
                "id": runner_id,
                "name": name,
                "age_group": age_group,
                "nationality": nationality,
                "UTMB Index": utmb_indexes,
                "club": club,
                "sponsor": sponsor,
                "races": races,
                "profile_url": runner_url
            }
            runners_data.append(runner_data)
            print(f"Scraped runner: {name} ({runner_id})")

        except Exception as e:
            print(f"Error scraping runner {runner_id}: {e}")

    save_data(RUNNER_JSON_PATH, runners_data)

def scrape_runners():
    if not get_page_with_retries(BASE_URL):
        return  # Stop if base URL fails to load

    existing_runner_ids = load_existing_data(RUNNER_ID_JSON_PATH, default=[])  # Load existing IDs
    all_runner_ids = set(existing_runner_ids)  # Use a set for quick lookup
    new_runner_ids = set()  # Store newly found IDs

    current_page = 1
    max_pages = get_max_pages()
    while current_page <= max_pages:
        print(f"Scraping Page {current_page}/{max_pages}")

        retries = 0
        while retries < MAX_RETRIES:
            runner_ids = extract_runner_ids()
            if runner_ids:
                break  # If we find runners, break out of the retry loop
            retries += 1
            print(f"Retrying Page {current_page}, attempt {retries}/{MAX_RETRIES}")
            time.sleep(2)  # Small delay before retrying
            get_page_with_retries(BASE_URL)  # Reload the page

        if not runner_ids:
            print(f"Skipping Page {current_page} due to no runner IDs found after {MAX_RETRIES} retries.")
            break  # If after max retries no IDs, exit loop

        for runner_id in runner_ids:
            if runner_id not in all_runner_ids:
                new_runner_ids.add(runner_id)  # Add only new IDs

        print(f"Found {len(runner_ids)} runner IDs on this page: {runner_ids}")

        # Click 'Next' if available
        next_buttons = driver.find_elements(By.CSS_SELECTOR, "a[class^='pagination_paginate_link__'][rel='next']")
        if not next_buttons or next_buttons[0].get_attribute("aria-disabled") == "true":
            print("No more pages to scrape.")
            break

        driver.execute_script("arguments[0].click();", next_buttons[0])
        current_page += 1

    if new_runner_ids:
        all_runner_ids.update(new_runner_ids)  # Merge new and existing IDs
        save_data(RUNNER_ID_JSON_PATH, list(all_runner_ids))  # Save as list
        print(f"New runner IDs added. Total: {len(all_runner_ids)}")

    # Scrape runner profiles
    scrape_runner_profiles(new_runner_ids)

    driver.quit()
    print("Scraping complete.")
if __name__ == "__main__":
    scrape_runners()
