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
CHROME_DRIVER_PATH = "./chromedriver"


def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=chrome_options)


def save_data(data):
    path = os.path.join(DATA_DIR, "raw_runner_id", f'runner_id_{datetime.datetime.now():%Y%m%d%H%M%S}.json')
    with open(path, "w") as file:
        json.dump(data, file, separators=(",", ":"))
    print(f"Saved {len(data)} runner IDs due to crash at {path}")


def get_page_with_retries(driver, url):
    attempt = 0
    while True:
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            if "503 Service Temporarily Unavailable" in driver.page_source:
                raise WebDriverException("503 Service Unavailable")
            return True
        except (TimeoutException, WebDriverException) as e:
            attempt += 1
            print(f"Attempt {attempt}: Error loading {url} - {e}")


def extract_runner_ids(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    runner_rows = soup.select(".my-table_row__nlm_j")
    runner_ids = []
    for row in runner_rows:
        link_elem = row.select_one("a[href*='/en/runner/']")
        if link_elem:
            runner_id = link_elem["href"].split("/")[-1]
            runner_ids.append(runner_id)
    return runner_ids


def find_resume_page(driver, last_runner_id, last_page_scraped):
    """Navigate pages until last runner ID is found."""
    page = 1

    # Fast forward to last scraped page
    while page < last_page_scraped:
        next_button = driver.find_elements(By.CSS_SELECTOR, "a[rel='next']")
        if not next_button or next_button[0].get_attribute("aria-disabled") == "true":
            print(f"Cannot reach last scraped page {last_page_scraped}.")
            return None
        driver.execute_script("arguments[0].click();", next_button[0])
        page += 1
        print(f"Skipping to page {page}")

    while True:
        print(f"Searching for last runner ID '{last_runner_id}' on page {page}...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".my-table_row__nlm_j")))
        ids = extract_runner_ids(driver)
        if not ids:
            print(f"No runner IDs found on page {page}, retrying...")
            continue

        if last_runner_id in ids:
            print(f"Found last runner ID on page {page}. Resuming from here.")
            return page

        next_button = driver.find_elements(By.CSS_SELECTOR, "a[rel='next']")
        if not next_button or next_button[0].get_attribute("aria-disabled") == "true":
            print("Reached end of pages but last ID not found.")
            return None

        driver.execute_script("arguments[0].click();", next_button[0])
        page += 1

def resume_scraping(num_pages, resume_from_runner_id=None, last_page_scraped=1):
    all_runner_ids = []
    last_runner_id = resume_from_runner_id
    found_resume_point = not bool(resume_from_runner_id)

    driver = setup_browser()

    try:
        if not get_page_with_retries(driver, BASE_URL):
            driver.quit()
            return

        max_pages = num_pages
        if num_pages == "max":
            soup = BeautifulSoup(driver.page_source, "html.parser")
            page_numbers = [int(link.text) for link in soup.select(".pagination_paginate_link__c9A6i") if link.text.isdigit()]
            max_pages = max(page_numbers) if page_numbers else 1

        current_page = 1

        if last_runner_id:
            page_found = find_resume_page(driver, last_runner_id, last_page_scraped)
            if not page_found:
                driver.quit()
                return
            else:
                current_page = page_found

        while current_page <= max_pages:
            runner_ids = []

            while len(runner_ids) == 0:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".my-table_row__nlm_j"))
                    )
                    runner_ids = extract_runner_ids(driver)
                    if len(runner_ids) == 0:
                        print(f"Retrying page {current_page} due to empty content.")
                except (TimeoutException, WebDriverException) as e:
                    print(f"Error on page {current_page}: {e}. Reloading browser")
                    break


            all_runner_ids.extend(runner_ids)
            if runner_ids:
                last_runner_id = runner_ids[-1]
                print(f"Page {current_page}: Collected {len(runner_ids)} runner IDs (Last: {last_runner_id})")

            current_page += 1

            next_button = driver.find_elements(By.CSS_SELECTOR, "a[rel='next']")
            if next_button and next_button[0].get_attribute("aria-disabled") != "true":
                driver.execute_script("arguments[0].click();", next_button[0])
            else:
                print("No more pages.")
                break

        driver.quit()
        print(f"Scraping finished. Total new runner IDs collected: {len(all_runner_ids)}")

    except Exception as e:
        print(f"Crash or error occurred: {e}")
        save_data(all_runner_ids)
        driver.quit()

        # Resume after crash
        if all_runner_ids:
            resume_scraping(num_pages, resume_from_runner_id=all_runner_ids[-1], last_page_scraped=current_page - 1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 runner_id_scraper.py <number of pages | 'max'>")
        sys.exit(1)

    arg = sys.argv[1]
    if arg.lower() == "max":
        NUM_PAGES = "max"
    else:
        try:
            NUM_PAGES = int(arg)
            if NUM_PAGES <= 0:
                raise ValueError
        except ValueError:
            print("Error: Enter a positive integer or 'max'")
            sys.exit(1)

    resume_scraping(NUM_PAGES)
