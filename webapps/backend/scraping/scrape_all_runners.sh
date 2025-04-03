#!/bin/bash

# Configuration
DATA_DIR="../../frontend/public/data/raw_runner_id"
INTERVAL=10000  # Split every 10,000 runners

# Ensure the data directory exists
mkdir -p "$DATA_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed."
    exit 1
fi

# Step 1: Scrape runner IDs
echo "Starting runner ID scraping..."
python3 runner_id_scraper.py "max"
if [ $? -ne 0 ]; then
    echo "Error: runner_id_scraper.py failed."
    exit 1
fi

# Find the latest runner_id JSON file
RUNNER_ID_JSON=$(ls -t "$DATA_DIR"/runner_id_*.json | head -n 1)

if [ -z "$RUNNER_ID_JSON" ]; then
    echo "Error: No runner_id JSON file found after scraping."
    exit 1
fi

echo "Latest runner ID file: $RUNNER_ID_JSON"

# Step 2: Split runner IDs
echo "Splitting runner ID JSON into chunks of $INTERVAL..."
python3 split_runner_id.py "$RUNNER_ID_JSON" "$INTERVAL"
if [ $? -ne 0 ]; then
    echo "Error: split_runner_id.py failed."
    exit 1
fi

# Step 3: Scrape runner profiles
echo "Starting runner profile scraping..."
for file in "${RUNNER_ID_JSON%.json}".*.json; do
    echo "Processing $file..."
    python3 runner_scraper.py "$file"
    if [ $? -ne 0 ]; then
        echo "Error: runner_scraper.py failed on $file."
        exit 1
    fi
done

echo "All tasks completed successfully!"
