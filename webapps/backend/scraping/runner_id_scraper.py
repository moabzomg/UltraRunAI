import sys
import os
import json
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configuration
BASE_URL = "https://utmb.world/utmb-index/runner-search"
DATA_DIR = "../../frontend/public/data"
RUNNER_ID_JSON_PATH = os.path.join(DATA_DIR, "raw_runner_id", f'runner_id_{datetime.datetime.now():%Y%m%d%H%M%S}.json')
CHROME_DRIVER_PATH = "./chromedriver"
MAX_RETRIES = 100  # Maximum retry attempts for 503 errors
NUM_PAGES = None  # Will be set by command-line argument


def setup_browser():
    """Set up a headless Chrome browser for Selenium."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=chrome_options)


def save_data(file_path, data):
    """Save the given data to a JSON file."""
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def get_page_with_retries(driver, url, max_retries=MAX_RETRIES):
    """Attempt to load a webpage, retrying if a 503 error occurs."""
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
    """Find the maximum number of pages available on the runner search."""
    max_pages = 1  # Default
    try:
        driver.get(BASE_URL)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Extract the highest available page number
        page_numbers = [int(link.text) for link in soup.select(".pagination_paginate_link__c9A6i") if link.text.isdigit()]
        if page_numbers:
            max_pages = max(page_numbers)
    except WebDriverException as e:
        print(f"Error finding max pages: {e}")

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


def scrape_runner_ids(num_pages):
    """Scrape runner IDs from multiple pages and save them periodically."""
    driver = setup_browser()
    if not get_page_with_retries(driver, BASE_URL):
        driver.quit()
        return

    all_runner_ids = []
    runner_ids = []
    max_pages = get_max_pages(driver)
    
    if num_pages == "max":
        num_pages = max_pages
    else:
        num_pages = min(num_pages, max_pages)

    print(f"Scraping up to {num_pages} pages (Max available: {max_pages})")

    for current_page in range(1, num_pages + 1):
        print(f"Scraping Page {current_page}/{num_pages}")

        # Wait for the current page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"a[aria-label='Page {current_page} is your current page']"))
        )

        # Extract runner IDs from the page
        runner_ids = extract_runner_ids(driver)
        all_runner_ids.extend(runner_ids)

        print(f"Found {len(runner_ids)} runners on page {current_page}")

        # Click 'Next' if available
        next_button = driver.find_elements(By.CSS_SELECTOR, "a[rel='next']")
        if next_button and next_button[0].get_attribute("aria-disabled") != "true":
            driver.execute_script("arguments[0].click();", next_button[0])
        else:
            print("No more pages to scrape.")
            break

    driver.quit()
    save_data(RUNNER_ID_JSON_PATH, all_runner_ids)
    print(f"Scraping completed. Total runners collected: {len(all_runner_ids)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 runner_id_scraper.py <number of pages | 'max' for all pages>")
        sys.exit(1)

    arg = sys.argv[1]

    # Validate argument
    if arg.lower() == "max":
        NUM_PAGES = "max"
    else:
        try:
            NUM_PAGES = int(arg)
            if NUM_PAGES <= 0:
                raise ValueError
        except ValueError:
            print("Error: The number of pages must be a positive integer or 'max'.")
            sys.exit(1)

    scrape_runner_ids(NUM_PAGES)
